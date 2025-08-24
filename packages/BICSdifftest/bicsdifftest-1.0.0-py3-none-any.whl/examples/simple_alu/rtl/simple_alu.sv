/*
 * Simple ALU Design for Differential Testing Framework Example
 * 
 * This module implements a basic arithmetic logic unit with multiple operations
 * to demonstrate the differential testing capabilities.
 */

module simple_alu #(
    parameter DATA_WIDTH = 32,
    parameter OP_WIDTH = 4
) (
    input  logic                    clk,
    input  logic                    rst_n,
    
    // Control interface
    input  logic                    valid_i,
    output logic                    ready_o,
    
    // Data interface  
    input  logic [DATA_WIDTH-1:0]   a_i,
    input  logic [DATA_WIDTH-1:0]   b_i,
    input  logic [OP_WIDTH-1:0]     op_i,
    
    // Output interface
    output logic [DATA_WIDTH-1:0]   result_o,
    output logic                    valid_o,
    output logic                    overflow_o,
    output logic                    zero_o,
    
    // Debug signals for differential testing
    output logic [DATA_WIDTH-1:0]   debug_stage1_o,
    output logic [DATA_WIDTH-1:0]   debug_stage2_o,
    output logic [3:0]              debug_flags_o
);

    // Operation codes
    typedef enum logic [OP_WIDTH-1:0] {
        ALU_ADD  = 4'b0000,
        ALU_SUB  = 4'b0001,
        ALU_MUL  = 4'b0010,
        ALU_DIV  = 4'b0011,
        ALU_AND  = 4'b0100,
        ALU_OR   = 4'b0101,
        ALU_XOR  = 4'b0110,
        ALU_NOT  = 4'b0111,
        ALU_SHL  = 4'b1000,
        ALU_SHR  = 4'b1001,
        ALU_ROL  = 4'b1010,
        ALU_ROR  = 4'b1011,
        ALU_MAX  = 4'b1100,
        ALU_MIN  = 4'b1101,
        ALU_CMP  = 4'b1110,
        ALU_NOP  = 4'b1111
    } alu_op_t;

    // Internal signals
    logic [DATA_WIDTH-1:0]   operand_a_reg;
    logic [DATA_WIDTH-1:0]   operand_b_reg;
    logic [OP_WIDTH-1:0]     operation_reg;
    logic                    input_valid_reg;
    
    logic [DATA_WIDTH-1:0]   stage1_result;
    logic [DATA_WIDTH-1:0]   stage2_result;
    logic [DATA_WIDTH-1:0]   final_result;
    
    logic                    stage1_overflow;
    logic                    stage2_overflow;
    logic                    final_overflow;
    
    logic                    computation_valid;
    logic [1:0]              pipeline_counter;

    // Ready signal - can accept new data when not processing
    assign ready_o = ~input_valid_reg;

    // Input registers
    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            operand_a_reg   <= '0;
            operand_b_reg   <= '0;
            operation_reg   <= ALU_NOP;
            input_valid_reg <= 1'b0;
        end else if (valid_i && ready_o) begin
            operand_a_reg   <= a_i;
            operand_b_reg   <= b_i;
            operation_reg   <= op_i;
            input_valid_reg <= 1'b1;
        end else if (computation_valid) begin
            input_valid_reg <= 1'b0;
        end
    end

    // Pipeline counter for multi-cycle operations
    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            pipeline_counter <= 2'b00;
        end else if (input_valid_reg) begin
            if (operation_reg == ALU_MUL || operation_reg == ALU_DIV) begin
                pipeline_counter <= pipeline_counter + 1;
            end else begin
                pipeline_counter <= 2'b11; // Single cycle completion
            end
        end else begin
            pipeline_counter <= 2'b00;
        end
    end

    assign computation_valid = (pipeline_counter == 2'b11) || 
                              ((operation_reg != ALU_MUL && operation_reg != ALU_DIV) && input_valid_reg);

    // Local variables for combinational logic
    logic [2*DATA_WIDTH-1:0] mul_result;
    logic [5:0] shift_amount;
    logic [5:0] rotate_amount;
    
    // Stage 1: Basic arithmetic and logic operations
    always_comb begin
        stage1_result = '0;
        stage1_overflow = 1'b0;
        mul_result = '0;
        
        case (operation_reg)
            ALU_ADD: begin
                {stage1_overflow, stage1_result} = operand_a_reg + operand_b_reg;
            end
            ALU_SUB: begin
                {stage1_overflow, stage1_result} = operand_a_reg - operand_b_reg;
            end
            ALU_MUL: begin
                // Simplified multiplier - would be more complex in real design
                mul_result = operand_a_reg * operand_b_reg;
                stage1_result = mul_result[DATA_WIDTH-1:0];
                stage1_overflow = |mul_result[2*DATA_WIDTH-1:DATA_WIDTH];
            end
            ALU_DIV: begin
                if (operand_b_reg != 0) begin
                    stage1_result = operand_a_reg / operand_b_reg;
                    stage1_overflow = 1'b0;
                end else begin
                    stage1_result = '1; // All 1s for divide by zero
                    stage1_overflow = 1'b1;
                end
            end
            ALU_AND: begin
                stage1_result = operand_a_reg & operand_b_reg;
            end
            ALU_OR: begin
                stage1_result = operand_a_reg | operand_b_reg;
            end
            ALU_XOR: begin
                stage1_result = operand_a_reg ^ operand_b_reg;
            end
            ALU_NOT: begin
                stage1_result = ~operand_a_reg;
            end
            default: begin
                stage1_result = operand_a_reg;
            end
        endcase
    end

    // Stage 2: Shift and rotation operations
    always_comb begin
        stage2_result = stage1_result;
        stage2_overflow = stage1_overflow;
        shift_amount = '0;
        rotate_amount = '0;
        
        case (operation_reg)
            ALU_SHL: begin
                shift_amount = operand_b_reg[5:0]; // Support up to 63-bit shifts
                if (shift_amount < DATA_WIDTH) begin
                    stage2_result = stage1_result << shift_amount;
                    stage2_overflow = |(stage1_result >> (DATA_WIDTH - shift_amount));
                end else begin
                    stage2_result = '0;
                    stage2_overflow = |stage1_result;
                end
            end
            ALU_SHR: begin
                shift_amount = operand_b_reg[5:0];
                if (shift_amount < DATA_WIDTH) begin
                    stage2_result = stage1_result >> shift_amount;
                end else begin
                    stage2_result = '0;
                end
            end
            ALU_ROL: begin
                rotate_amount = operand_b_reg[5:0] % DATA_WIDTH;
                stage2_result = (stage1_result << rotate_amount) | 
                               (stage1_result >> (DATA_WIDTH - rotate_amount));
            end
            ALU_ROR: begin
                rotate_amount = operand_b_reg[5:0] % DATA_WIDTH;
                stage2_result = (stage1_result >> rotate_amount) | 
                               (stage1_result << (DATA_WIDTH - rotate_amount));
            end
            ALU_MAX: begin
                stage2_result = (operand_a_reg > operand_b_reg) ? operand_a_reg : operand_b_reg;
            end
            ALU_MIN: begin
                stage2_result = (operand_a_reg < operand_b_reg) ? operand_a_reg : operand_b_reg;
            end
            ALU_CMP: begin
                if (operand_a_reg == operand_b_reg) begin
                    stage2_result = 32'h00000000;
                end else if (operand_a_reg > operand_b_reg) begin
                    stage2_result = 32'h00000001;
                end else begin
                    stage2_result = 32'hFFFFFFFF;
                end
            end
            default: begin
                stage2_result = stage1_result;
            end
        endcase
    end

    // Final stage: Output registers
    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            final_result   <= '0;
            final_overflow <= 1'b0;
            valid_o        <= 1'b0;
        end else if (computation_valid) begin
            final_result   <= stage2_result;
            final_overflow <= stage2_overflow;
            valid_o        <= 1'b1;
        end else begin
            valid_o        <= 1'b0;
        end
    end

    // Output assignments
    assign result_o   = final_result;
    assign overflow_o = final_overflow;
    assign zero_o     = (final_result == '0);

    // Debug outputs for differential testing
    assign debug_stage1_o = stage1_result;
    assign debug_stage2_o = stage2_result;
    assign debug_flags_o  = {final_overflow, zero_o, computation_valid, input_valid_reg};

    // Assertions for verification
    `ifdef SIMULATION
        // Check that ready is deasserted when processing
        assert property (@(posedge clk) disable iff (!rst_n) 
                        input_valid_reg |-> !ready_o);
        
        // Check that valid output is only asserted for one cycle
        assert property (@(posedge clk) disable iff (!rst_n)
                        valid_o |=> !valid_o [*0:2]);
        
        // Check overflow behavior for addition
        assert property (@(posedge clk) disable iff (!rst_n)
                        (computation_valid && operation_reg == ALU_ADD) |->
                        (overflow_o == (operand_a_reg + operand_b_reg > {1'b1, {DATA_WIDTH{1'b1}}})));
    `endif

endmodule
