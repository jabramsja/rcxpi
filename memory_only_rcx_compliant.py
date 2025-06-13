
"""memory_only_rcx_compliant.py – fully RCX‑π compliant sandbox"""
import struct, hashlib, time
MAX_RULES = 1024
MAX_MEM_BYTES = 1 << 20
DEFAULT_WAIT = 10

class MemorySpace:
    def __init__(self):
        self.data = bytearray(b'\x00')
    def grow_to(self, pos:int):
        if pos >= MAX_MEM_BYTES:
            raise MemoryError("cap")
        need = pos - len(self.data)+1
        if need>0:
            self.data.extend(b'\x00'*need)
    def get_mem(self,pos:int)->int:
        self.grow_to(pos)
        return self.data[pos]
    def set_mem(self,pos:int,val:int):
        self.grow_to(pos)
        self.data[pos]=val & 0xFF

class MemoryOperations:
    def __init__(self):
        self.mem = MemorySpace()
        self.rule_mem = bytearray(5*MAX_RULES)
        self.gate_table=[self._no_op]*MAX_RULES
        self.divergence_log=[]
        self._fix_state={}
    # primitives
    def _nabla_r(self,p): _=self.mem.get_mem(p)
    def _delta(self,p):
        v=self.mem.get_mem(p)
        self.mem.set_mem(p,v^0xFF)
    def _fix(self,p):
        addr=p
        wait=DEFAULT_WAIT or 10
        dig=hashlib.blake2b(bytes(self.mem.data[addr:addr+16]),digest_size=8).digest()
        last,cnt=self._fix_state.get(addr,(None,0))
        if dig==last: cnt+=1
        else: cnt=0
        self._fix_state[addr]=(dig,cnt)
    def _no_op(self,p): pass
    # rule mgmt
    def build_gate_from_rule(self,rid:int):
        op=self.rule_mem[rid*5]
        arg=struct.unpack_from('<I',self.rule_mem,rid*5+1)[0]
        fn={0:self._nabla_r,1:self._delta,2:self._fix}.get(op,self._no_op)
        self.gate_table[rid]= (lambda p=arg,f=fn: f(p))
    def mutate_rule(self,rid:int, rule:bytes):
        if not(0<=rid<MAX_RULES): raise IndexError
        if len(rule)!=5: raise ValueError
        self.rule_mem[rid*5:rid*5+5]=rule
        self.build_gate_from_rule(rid)
        self.log_divergence(rid,rule)
    def log_divergence(self,rid,b): self.divergence_log.append((time.time(),rid,b))

class RCXSystem:
    def __init__(self): self.ops=MemoryOperations()
    def gate_dispatch(self,rid:int): self.ops.gate_table[rid](rid)
    def run_continuous(self,manual_halt_after=None):
        it=0
        while manual_halt_after is None or it<manual_halt_after:
            for rid in range(MAX_RULES): self.gate_dispatch(rid)
            it+=1
        return {"iters":it,"hash":self.hash_state()}
    def hash_state(self)->str:
        return hashlib.blake2b(bytes(self.ops.mem.data),digest_size=16).hexdigest()
    def emit_full_seed(self,n:int)->bytes: return self.emit_seed(n)
    def emit_seed(self,n:int)->bytes:
        return b"RCX\x00"+struct.pack('<Q',n)+self.ops.rule_mem[:n*5]
