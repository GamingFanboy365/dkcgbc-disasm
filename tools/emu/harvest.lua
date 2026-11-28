-- Visit sample points in every level and log what each live object uses.
-- env: JOBS (file), PART (k), PARTS (n), OUT (log file), RUN (frames per job),
-- MODE (idle, right, left, roll, slap, up, swim), KONG (diddy), SILENCE (1)
local KEY={A=1,B=2,SELECT=4,START=8,RIGHT=16,LEFT=32,UP=64,DOWN=128}
local steps = { {900,"A",5},{600,"",0},{3000,"START",5},{300,"A",5},{200,"A",5},{800,"A",5},{390,"",0} }
local PART=tonumber(os.getenv("PART")); local PARTS=tonumber(os.getenv("PARTS"))
local jobs={}
local n=0
for line in io.lines(os.getenv("JOBS")) do
  if n % PARTS == PART then
    local d,c,x,y,v,rest=line:match("(%x+) (%x+) (%x+) (%x+) (%x+)(.*)")
    local chain={}
    for th,fl in rest:gmatch(" (%x+) (%x+)") do chain[#chain+1]={tonumber(th,16),tonumber(fl,16)} end
    jobs[#jobs+1]={tonumber(d,16),tonumber(c,16),tonumber(x,16),tonumber(y,16),tonumber(v,16),n,chain}
  end
  n=n+1
end
local log=io.open(os.getenv("OUT"),"w")
local cart=emu.memory.cart0
local E=0x585c            -- scratch entrance record (bank 4)
local function rom4(a) return 4*0x4000+a-0x4000 end
-- every level number enters through the scratch record
for lv=1,0x29 do
  local p=rom4(0x57b4+4*lv)
  if cart:read8(p)+cart:read8(p+1)>0 then
    cart:write8(p,E&0xff); cart:write8(p+1,E>>8); cart:write8(p+2,E&0xff); cart:write8(p+3,E>>8)
  end
end
local frame, si, hold, holdmask = 0,1,0,0
local waiting = steps[1][1]
local state=nil
local ji=0
local t=0
local seen={}
local forced=0      -- pairs of the job's chain applied so far
local forcedat=0
local KONG=os.getenv("KONG")   -- "diddy": play as Diddy Kong
local lastpal=""
local RUN=tonumber(os.getenv("RUN") or "330")
local MODE=os.getenv("MODE") or "idle"
local function hex(s) return (s:gsub(".", function(c) return string.format("%02x", c:byte()) end)) end
local function startjob()
  ji=ji+1
  if ji>#jobs then log:close(); os.exit(0) end
  local j=jobs[ji]
  emu:loadStateBuffer(state)
  local o=rom4(E)
  local rec={j[1]&0xff,j[1]>>8,j[2],j[3]&0xff,j[3]>>8,j[4]&0xff,j[4]>>8,j[5]}
  for k=1,8 do cart:write8(o+k-1,rec[k]) end
  log:write(string.format("J %d %04x %04x %04x\n", j[6], j[1], j[3], j[4]))
  t=0; seen={}; lastpal=""; forced=0; forcedat=0
  if KONG=="diddy" then emu:write8(0xc30f, emu:read8(0xc30f)|1) end
end
-- apply an initialiser list (bank 9) to a live object, as ApplyObjInit would
local function applylist(slot, addr, depth)
  local o=9*0x4000+addr-0x4000
  while depth<6 do
    local b=cart:read8(o)
    if b<0x40 then emu:write8(0xc800+slot*64+b, cart:read8(o+1)); o=o+2
    elseif b<0x80 then emu:write8(0xc800+slot*64+(b&0x3f), cart:read8(o+1)); emu:write8(0xc800+slot*64+(b&0x3f)+1, cart:read8(o+2)); o=o+3
    elseif b==0x80 then applylist(slot, cart:read8(o+1)+cart:read8(o+2)*256, depth+1); o=o+3
    else break end
  end
end
-- next pair of the job's chain: (touch handler, list) -- the list is applied
-- to every live object with that touch handler, 150 frames in at the
-- earliest and 70 frames after the pair before it
local function force()
  local pair=jobs[ji][7][forced+1]
  if not pair or t<forcedat+70 then return end
  local objs=emu:readRange(0xc800,0x800)
  local hit=false
  for s=1,31 do
    local b=s*64
    if objs:byte(b+1)~=0 and objs:byte(b+5)+objs:byte(b+6)*256==pair[1] then applylist(s, pair[2], 0); hit=true; log:write("F "..t.." "..s.."\n") end
  end
  if hit then forced=forced+1; forcedat=t end
end
local function sample()
  local pal=emu:readRange(0xc280,64)
  if pal~=lastpal then lastpal=pal; log:write("P "..t.." "..hex(pal).."\n") end
  local objs=emu:readRange(0xc800,0x800)
  for s=0,31 do
    local b=s*64
    local fl=objs:byte(b+1)
    if fl~=0 then
      local bank=objs:byte(b+2); local h=objs:byte(b+3)+objs:byte(b+4)*256
      local th=objs:byte(b+5)+objs:byte(b+6)*256
      local attr=objs:byte(b+0x20); local fr=objs:byte(b+0x21)+objs:byte(b+0x22)*256
      local an=objs:byte(b+0x23)+objs:byte(b+0x24)*256
      local sp=objs:byte(b+0x28); local pf=objs:byte(b+0x2b)
      local key=string.format("%d %02x %04x %04x %02x %02x %04x %04x %02x", s, bank, h, th, attr, pf, fr, an, sp)
      if not seen[key] then
        seen[key]=true
        local ip, sf = 0, 0
        if sp~=0 then
          sf=emu.memory.sram:read8(0x0800+sp)
          ip=emu.memory.sram:read8(0x0d00+sp)+emu.memory.sram:read8(0x0e00+sp)*256
        end
        log:write(string.format("O %d %s %02x %04x\n", t, key, sf, ip))
      end
    end
  end
end
callbacks:add("frame", function()
  frame=frame+1
  if state then
    t=t+1
    local k=0
    if t<=5 then k=KEY.A
    elseif t>60 and MODE=="right" then k=KEY.RIGHT; if t%45<12 then k=k|KEY.A end
    elseif t>60 and MODE=="left" then k=KEY.LEFT; if t%45<12 then k=k|KEY.A end
    elseif t>60 and MODE=="roll" then if t%30<4 then k=KEY.B|KEY.RIGHT elseif t%30<20 then k=KEY.RIGHT end
    elseif t>60 and MODE=="slap" then k=KEY.DOWN; if t%60>=30 and t%60<34 then k=k|KEY.B end   -- crouch, hand slap
    elseif t>60 and MODE=="up" then k=KEY.UP; if t%90<6 then k=k|KEY.A end                    -- climb, look up
    elseif t>60 and MODE=="swim" then k=KEY.RIGHT; if t%16<4 then k=k|KEY.A end; if t%120>=100 then k=k|KEY.B end
    end
    emu:setKeys(k)
    if t>=150 then force() end
    -- SILENCE=1: from frame 700, mark the music as finished every second, so
    -- scenes that wait for a song to end go on (K. Rool's fake Kredits)
    if os.getenv("SILENCE")=="1" and t>=700 and t%60==0 then
      for c=0,3 do emu.memory.wram:write8(4*0x1000+c*0x100+0x1f, 0) end
    end
    if t>=40 then sample() end
    if t>=RUN then startjob() end
    return
  end
  if hold>0 then hold=hold-1; emu:setKeys(holdmask); if hold==0 then emu:setKeys(0) end; return end
  if waiting>0 then waiting=waiting-1; return end
  local st=steps[si]
  if not st then state=emu:saveStateBuffer(); startjob(); return end
  if st[2]~="" then holdmask=0; for k in st[2]:gmatch("%a+") do holdmask=holdmask|KEY[k] end; hold=st[3]; emu:setKeys(holdmask) end
  si=si+1; waiting=steps[si] and steps[si][1] or 0
end)
