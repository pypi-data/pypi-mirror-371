/* verilator lint_off DECLFILENAME */
module FPU (
    input [31:0] a,
    input [31:0] b,
    output reg [31:0] result
);

    always @(*) begin
        if (a > b) begin
            result = a;
        end else begin
            result = b;
        end
    end

endmodule
/* verilator lint_on DECLFILENAME */
