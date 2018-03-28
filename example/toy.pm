dtmc

param int p;
param int q;

module toy


s : [0..5];

[] s=0 -> 0.5 : (s'=1) + 0.5 : (s'=3);
[] s=1 -> p : (s'=0) + q : (s'=1) + (1-p-q) : (s'=2);
[] s=3 -> p : (s'=2) + q : (s'=4) + (1-p-q) : (s'=3);

endmodule


rewards
    []s=4 : 1;
endrewards

