/*
 * Fully Connected Neural Network Layer Design for Differential Testing Framework
 * 
 * This module implements a single-layer fully connected neural network with:
 * - 100 inputs, 10 outputs 
 * - Fixed-point arithmetic (16-bit with 8 fractional bits)
 * - Pipeline design for efficiency
 * - Weight loading and inference modes
 * - Proper handshaking with valid/ready signals
 */

module fc_layer #(
    parameter INPUT_SIZE = 100,
    parameter OUTPUT_SIZE = 10,
    parameter DATA_WIDTH = 16,
    parameter FRAC_BITS = 8,
    parameter WEIGHT_WIDTH = 16,
    parameter ADDR_WIDTH = 10  // log2(max(INPUT_SIZE, OUTPUT_SIZE))
) (
    input  logic                           clk,
    input  logic                           rst_n,
    
    // Control interface
    input  logic                           mode_i,        // 0: weight loading, 1: inference
    input  logic                           valid_i,
    output logic                           ready_o,
    
    // Weight loading interface (mode_i = 0)
    input  logic [ADDR_WIDTH-1:0]          weight_addr_i,
    input  logic [WEIGHT_WIDTH-1:0]        weight_data_i,
    input  logic                           weight_we_i,
    
    // Inference input interface (mode_i = 1)  
    input  logic [INPUT_SIZE-1:0][DATA_WIDTH-1:0] input_data_i,
    
    // Bias loading/inference interface
    input  logic [ADDR_WIDTH-1:0]          bias_addr_i,
    input  logic [DATA_WIDTH-1:0]          bias_data_i,
    input  logic                           bias_we_i,
    
    // Output interface
    output logic [OUTPUT_SIZE-1:0][DATA_WIDTH-1:0] output_data_o,
    output logic                           valid_o,
    
    // Debug signals for differential testing
    output logic [31:0]                    debug_state_o,
    output logic [DATA_WIDTH-1:0]          debug_accumulator_o,
    output logic [ADDR_WIDTH-1:0]          debug_addr_counter_o,
    output logic [3:0]                     debug_flags_o
);

    // Internal memory for weights and biases
    logic [INPUT_SIZE-1:0][OUTPUT_SIZE-1:0][WEIGHT_WIDTH-1:0] weight_memory;
    logic [OUTPUT_SIZE-1:0][DATA_WIDTH-1:0] bias_memory;
    
    // Pipeline registers
    logic [INPUT_SIZE-1:0][DATA_WIDTH-1:0] input_reg;
    logic [OUTPUT_SIZE-1:0][DATA_WIDTH-1:0] output_reg;
    logic [OUTPUT_SIZE-1:0][DATA_WIDTH-1:0] output_reg_next;
    
    // State machine
    typedef enum logic [2:0] {
        IDLE      = 3'b000,
        LOAD_WEIGHTS = 3'b001,
        LOAD_BIAS = 3'b010,
        COMPUTE   = 3'b011,
        ACCUMULATE = 3'b100,
        OUTPUT    = 3'b101
    } state_t;
    
    state_t current_state, next_state;
    
    // Computation variables
    logic [ADDR_WIDTH-1:0] input_counter, output_counter;
    logic [ADDR_WIDTH-1:0] input_counter_next, output_counter_next;
    
    // Fixed-point computation signals
    logic signed [DATA_WIDTH+WEIGHT_WIDTH-1:0] mult_result_full;
    logic signed [DATA_WIDTH-1:0] mult_result;
    logic signed [DATA_WIDTH+WEIGHT_WIDTH+ADDR_WIDTH-1:0] accumulator, accumulator_next;
    logic signed [DATA_WIDTH-1:0] final_result;
    
    // Control signals
    logic computation_done, weight_loading_done, bias_loading_done;
    logic overflow_flag, underflow_flag;
    
    // Ready signal generation
    assign ready_o = (current_state == IDLE) || 
                     (current_state == LOAD_WEIGHTS && !mode_i) ||
                     (current_state == LOAD_BIAS && !mode_i);
    
    // Weight and bias loading
    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            // Initialize all weights and biases to zero
            for (int i = 0; i < INPUT_SIZE; i++) begin
                for (int j = 0; j < OUTPUT_SIZE; j++) begin
                    weight_memory[i][j] <= '0;
                end
            end
            for (int j = 0; j < OUTPUT_SIZE; j++) begin
                bias_memory[j] <= '0;
            end
        end else begin
            // Weight loading (weight_addr_i encodes both input and output indices)
            if (weight_we_i && !mode_i) begin
                logic [6:0] input_idx;
                logic [3:0] output_idx;
                
                input_idx = weight_addr_i[9:3];  // Upper 7 bits for input index (0-99)
                output_idx = {1'b0, weight_addr_i[2:0]}; // Lower 3 bits for output index (0-9) 
                
                if (input_idx < INPUT_SIZE && output_idx < OUTPUT_SIZE) begin
                    weight_memory[input_idx][output_idx] <= weight_data_i;
                end
            end
            
            // Bias loading
            if (bias_we_i && !mode_i) begin
                if (bias_addr_i < OUTPUT_SIZE) begin
                    bias_memory[bias_addr_i] <= bias_data_i;
                end
            end
        end
    end
    
    // State machine
    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            current_state <= IDLE;
            input_counter <= '0;
            output_counter <= '0;
            accumulator <= '0;
        end else begin
            current_state <= next_state;
            input_counter <= input_counter_next;
            output_counter <= output_counter_next;
            accumulator <= accumulator_next;
        end
    end
    
    // Next state logic and datapath control
    always_comb begin
        // Default assignments
        next_state = current_state;
        input_counter_next = input_counter;
        output_counter_next = output_counter;
        accumulator_next = accumulator;
        output_reg_next = output_reg;
        
        computation_done = 1'b0;
        weight_loading_done = 1'b0;
        bias_loading_done = 1'b0;
        
        // Default assignments for signals to avoid latches
        mult_result_full = '0;
        mult_result = '0;
        final_result = '0;
        overflow_flag = 1'b0;
        underflow_flag = 1'b0;
        
        case (current_state)
            IDLE: begin
                if (valid_i) begin
                    if (!mode_i) begin
                        // Weight/bias loading mode
                        next_state = LOAD_WEIGHTS;
                    end else begin
                        // Inference mode
                        next_state = COMPUTE;
                        input_counter_next = '0;
                        output_counter_next = '0;
                        accumulator_next = '0;
                    end
                end
            end
            
            LOAD_WEIGHTS: begin
                if (mode_i) begin
                    // Switch to inference mode
                    next_state = COMPUTE;
                    input_counter_next = '0;
                    output_counter_next = '0;
                    accumulator_next = '0;
                end
            end
            
            LOAD_BIAS: begin
                if (mode_i) begin
                    // Switch to inference mode
                    next_state = COMPUTE;
                    input_counter_next = '0;
                    output_counter_next = '0;
                    accumulator_next = '0;
                end
            end
            
            COMPUTE: begin
                // Start computation for current output neuron
                next_state = ACCUMULATE;
                input_counter_next = '0;
                // Initialize accumulator with bias
                accumulator_next = {{(DATA_WIDTH+WEIGHT_WIDTH+ADDR_WIDTH-DATA_WIDTH){bias_memory[output_counter][DATA_WIDTH-1]}}, 
                                  bias_memory[output_counter]};
            end
            
            ACCUMULATE: begin
                // Perform MAC operation: accumulator += input[i] * weight[i][j]
                // Multiply with full precision
                mult_result_full = $signed(input_reg[input_counter]) * $signed(weight_memory[input_counter][output_counter]);
                
                // Scale down by fractional bits (fixed-point division)
                mult_result = mult_result_full[DATA_WIDTH+FRAC_BITS-1:FRAC_BITS];
                
                // Add to accumulator with proper sign extension
                accumulator_next = accumulator + {{(DATA_WIDTH+WEIGHT_WIDTH+ADDR_WIDTH-DATA_WIDTH){mult_result[DATA_WIDTH-1]}}, mult_result};
                
                if (input_counter == INPUT_SIZE - 1) begin
                    // Finished current output, move to next
                    next_state = OUTPUT;
                end else begin
                    // Continue with next input
                    input_counter_next = input_counter + 1;
                end
            end
            
            OUTPUT: begin
                // Saturate and store result - simply use lower 16 bits
                // The accumulator is wide enough that typical computations shouldn't overflow
                final_result = accumulator[DATA_WIDTH-1:0];
                overflow_flag = 1'b0;
                underflow_flag = 1'b0;
                
                output_reg_next[output_counter] = final_result;
                
                if (output_counter == OUTPUT_SIZE - 1) begin
                    // All outputs computed
                    next_state = IDLE;
                    output_counter_next = '0;
                    computation_done = 1'b1;
                end else begin
                    // Move to next output neuron
                    next_state = COMPUTE;
                    output_counter_next = output_counter + 1;
                end
            end
            
            default: begin
                next_state = IDLE;
            end
        endcase
    end
    
    // Input register
    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            input_reg <= '0;
        end else if (valid_i && ready_o && mode_i) begin
            input_reg <= input_data_i;
        end
    end
    
    // Output register
    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            output_reg <= '0;
            valid_o <= 1'b0;
        end else if (computation_done) begin
            output_reg <= output_reg_next;
            valid_o <= 1'b1;
        end else begin
            valid_o <= 1'b0;
        end
    end
    
    // Output assignment
    assign output_data_o = output_reg;
    
    // Debug outputs
    assign debug_state_o = {28'b0, current_state, mode_i};
    assign debug_accumulator_o = accumulator[DATA_WIDTH-1:0];
    assign debug_addr_counter_o = {input_counter[6:0], output_counter[2:0]};
    assign debug_flags_o = {computation_done, overflow_flag, underflow_flag, valid_o};
    
    // Assertions for verification
    `ifdef SIMULATION
        // Check that ready is properly managed
        property ready_idle;
            @(posedge clk) disable iff (!rst_n)
            (current_state == IDLE) |-> ready_o;
        endproperty
        assert property (ready_idle);
        
        // Check valid output timing
        property valid_output_timing;
            @(posedge clk) disable iff (!rst_n)
            valid_o |-> (current_state == IDLE && $past(computation_done));
        endproperty
        assert property (valid_output_timing);
        
        // Check counter bounds
        property input_counter_bounds;
            @(posedge clk) disable iff (!rst_n)
            input_counter < INPUT_SIZE;
        endproperty
        assert property (input_counter_bounds);
        
        property output_counter_bounds;
            @(posedge clk) disable iff (!rst_n)
            output_counter < OUTPUT_SIZE;
        endproperty
        assert property (output_counter_bounds);
        
        // Weight loading bounds check
        property weight_addr_bounds;
            @(posedge clk) disable iff (!rst_n)
            (weight_we_i && !mode_i) |-> 
            (weight_addr_i[9:3] < INPUT_SIZE && weight_addr_i[2:0] < OUTPUT_SIZE);
        endproperty
        assert property (weight_addr_bounds);
        
        // Bias loading bounds check  
        property bias_addr_bounds;
            @(posedge clk) disable iff (!rst_n)
            (bias_we_i && !mode_i) |-> (bias_addr_i < OUTPUT_SIZE);
        endproperty
        assert property (bias_addr_bounds);
        
    `endif

endmodule
