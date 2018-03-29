dtmc

param int p;
module toy


s : [0..3];

[] s=0 -> p : (s'=1) + (1-p) : (s'=2);

endmodule


rewards
[]s=2 : 1;
endrewards

