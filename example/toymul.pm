
dtmc

const int N = 100;
param int q;
param int p{0..N};


module toy

par : [0..N];
s : [0..5];

[] s=0 & par < N -> 0.5 : (s'=1) + 0.5 : (s'=3);
[] s=1 & par < N -> p{par} : (s'=0) + q : (s'=1) & (par'=par+1) + (1-p{par}-q) : (s'=2) & (par'=par+1);
[] s=3 & par < N-> p{par} : (s'=2) + q : (s'=4) & (par'=par+1) + (1-p{par}-q) : (s'=3) & (par'=par+1);
[] par=N -> (par'=0);
endmodule


rewards
[]s=4 : 1;
endrewards
