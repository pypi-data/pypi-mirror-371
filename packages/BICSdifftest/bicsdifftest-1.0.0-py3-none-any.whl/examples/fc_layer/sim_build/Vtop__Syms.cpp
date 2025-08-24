// Verilated -*- C++ -*-
// DESCRIPTION: Verilator output: Symbol table implementation internals

#include "Vtop__pch.h"
#include "Vtop.h"
#include "Vtop___024root.h"

// FUNCTIONS
Vtop__Syms::~Vtop__Syms()
{

    // Tear down scope hierarchy
    __Vhier.remove(0, &__Vscope_fc_layer);
    __Vhier.remove(&__Vscope_fc_layer, &__Vscope_fc_layer__unnamedblk1);
    __Vhier.remove(&__Vscope_fc_layer, &__Vscope_fc_layer__unnamedblk3);
    __Vhier.remove(&__Vscope_fc_layer, &__Vscope_fc_layer__unnamedblk4);
    __Vhier.remove(&__Vscope_fc_layer__unnamedblk1, &__Vscope_fc_layer__unnamedblk1__unnamedblk2);

}

Vtop__Syms::Vtop__Syms(VerilatedContext* contextp, const char* namep, Vtop* modelp)
    : VerilatedSyms{contextp}
    // Setup internal state of the Syms class
    , __Vm_modelp{modelp}
    // Setup module instances
    , TOP{this, namep}
{
        // Check resources
        Verilated::stackCheck(49);
    // Configure time unit / time precision
    _vm_contextp__->timeunit(-9);
    _vm_contextp__->timeprecision(-12);
    // Setup each module's pointers to their submodules
    // Setup each module's pointer back to symbol table (for public functions)
    TOP.__Vconfigure(true);
    // Setup scopes
    __Vscope_TOP.configure(this, name(), "TOP", "TOP", "<null>", 0, VerilatedScope::SCOPE_OTHER);
    __Vscope_fc_layer.configure(this, name(), "fc_layer", "fc_layer", "fc_layer", -9, VerilatedScope::SCOPE_MODULE);
    __Vscope_fc_layer__unnamedblk1.configure(this, name(), "fc_layer.unnamedblk1", "unnamedblk1", "<null>", -9, VerilatedScope::SCOPE_OTHER);
    __Vscope_fc_layer__unnamedblk1__unnamedblk2.configure(this, name(), "fc_layer.unnamedblk1.unnamedblk2", "unnamedblk2", "<null>", -9, VerilatedScope::SCOPE_OTHER);
    __Vscope_fc_layer__unnamedblk3.configure(this, name(), "fc_layer.unnamedblk3", "unnamedblk3", "<null>", -9, VerilatedScope::SCOPE_OTHER);
    __Vscope_fc_layer__unnamedblk4.configure(this, name(), "fc_layer.unnamedblk4", "unnamedblk4", "<null>", -9, VerilatedScope::SCOPE_OTHER);

    // Set up scope hierarchy
    __Vhier.add(0, &__Vscope_fc_layer);
    __Vhier.add(&__Vscope_fc_layer, &__Vscope_fc_layer__unnamedblk1);
    __Vhier.add(&__Vscope_fc_layer, &__Vscope_fc_layer__unnamedblk3);
    __Vhier.add(&__Vscope_fc_layer, &__Vscope_fc_layer__unnamedblk4);
    __Vhier.add(&__Vscope_fc_layer__unnamedblk1, &__Vscope_fc_layer__unnamedblk1__unnamedblk2);

    // Setup export functions
    for (int __Vfinal = 0; __Vfinal < 2; ++__Vfinal) {
        __Vscope_TOP.varInsert(__Vfinal,"bias_addr_i", &(TOP.bias_addr_i), false, VLVT_UINT16,VLVD_IN|VLVF_PUB_RW,0,1 ,9,0);
        __Vscope_TOP.varInsert(__Vfinal,"bias_data_i", &(TOP.bias_data_i), false, VLVT_UINT16,VLVD_IN|VLVF_PUB_RW,0,1 ,15,0);
        __Vscope_TOP.varInsert(__Vfinal,"bias_we_i", &(TOP.bias_we_i), false, VLVT_UINT8,VLVD_IN|VLVF_PUB_RW,0,0);
        __Vscope_TOP.varInsert(__Vfinal,"clk", &(TOP.clk), false, VLVT_UINT8,VLVD_IN|VLVF_PUB_RW,0,0);
        __Vscope_TOP.varInsert(__Vfinal,"debug_accumulator_o", &(TOP.debug_accumulator_o), false, VLVT_UINT16,VLVD_OUT|VLVF_PUB_RW,0,1 ,15,0);
        __Vscope_TOP.varInsert(__Vfinal,"debug_addr_counter_o", &(TOP.debug_addr_counter_o), false, VLVT_UINT16,VLVD_OUT|VLVF_PUB_RW,0,1 ,9,0);
        __Vscope_TOP.varInsert(__Vfinal,"debug_flags_o", &(TOP.debug_flags_o), false, VLVT_UINT8,VLVD_OUT|VLVF_PUB_RW,0,1 ,3,0);
        __Vscope_TOP.varInsert(__Vfinal,"debug_state_o", &(TOP.debug_state_o), false, VLVT_UINT32,VLVD_OUT|VLVF_PUB_RW,0,1 ,31,0);
        __Vscope_TOP.varInsert(__Vfinal,"input_data_i", &(TOP.input_data_i), false, VLVT_WDATA,VLVD_IN|VLVF_PUB_RW,0,2 ,99,0 ,15,0);
        __Vscope_TOP.varInsert(__Vfinal,"mode_i", &(TOP.mode_i), false, VLVT_UINT8,VLVD_IN|VLVF_PUB_RW,0,0);
        __Vscope_TOP.varInsert(__Vfinal,"output_data_o", &(TOP.output_data_o), false, VLVT_WDATA,VLVD_OUT|VLVF_PUB_RW,0,2 ,9,0 ,15,0);
        __Vscope_TOP.varInsert(__Vfinal,"ready_o", &(TOP.ready_o), false, VLVT_UINT8,VLVD_OUT|VLVF_PUB_RW,0,0);
        __Vscope_TOP.varInsert(__Vfinal,"rst_n", &(TOP.rst_n), false, VLVT_UINT8,VLVD_IN|VLVF_PUB_RW,0,0);
        __Vscope_TOP.varInsert(__Vfinal,"valid_i", &(TOP.valid_i), false, VLVT_UINT8,VLVD_IN|VLVF_PUB_RW,0,0);
        __Vscope_TOP.varInsert(__Vfinal,"valid_o", &(TOP.valid_o), false, VLVT_UINT8,VLVD_OUT|VLVF_PUB_RW,0,0);
        __Vscope_TOP.varInsert(__Vfinal,"weight_addr_i", &(TOP.weight_addr_i), false, VLVT_UINT16,VLVD_IN|VLVF_PUB_RW,0,1 ,9,0);
        __Vscope_TOP.varInsert(__Vfinal,"weight_data_i", &(TOP.weight_data_i), false, VLVT_UINT16,VLVD_IN|VLVF_PUB_RW,0,1 ,15,0);
        __Vscope_TOP.varInsert(__Vfinal,"weight_we_i", &(TOP.weight_we_i), false, VLVT_UINT8,VLVD_IN|VLVF_PUB_RW,0,0);
        __Vscope_fc_layer.varInsert(__Vfinal,"ADDR_WIDTH", const_cast<void*>(static_cast<const void*>(&(TOP.fc_layer__DOT__ADDR_WIDTH))), true, VLVT_UINT32,VLVD_NODIR|VLVF_PUB_RW,0,1 ,31,0);
        __Vscope_fc_layer.varInsert(__Vfinal,"DATA_WIDTH", const_cast<void*>(static_cast<const void*>(&(TOP.fc_layer__DOT__DATA_WIDTH))), true, VLVT_UINT32,VLVD_NODIR|VLVF_PUB_RW,0,1 ,31,0);
        __Vscope_fc_layer.varInsert(__Vfinal,"FRAC_BITS", const_cast<void*>(static_cast<const void*>(&(TOP.fc_layer__DOT__FRAC_BITS))), true, VLVT_UINT32,VLVD_NODIR|VLVF_PUB_RW,0,1 ,31,0);
        __Vscope_fc_layer.varInsert(__Vfinal,"INPUT_SIZE", const_cast<void*>(static_cast<const void*>(&(TOP.fc_layer__DOT__INPUT_SIZE))), true, VLVT_UINT32,VLVD_NODIR|VLVF_PUB_RW,0,1 ,31,0);
        __Vscope_fc_layer.varInsert(__Vfinal,"OUTPUT_SIZE", const_cast<void*>(static_cast<const void*>(&(TOP.fc_layer__DOT__OUTPUT_SIZE))), true, VLVT_UINT32,VLVD_NODIR|VLVF_PUB_RW,0,1 ,31,0);
        __Vscope_fc_layer.varInsert(__Vfinal,"WEIGHT_WIDTH", const_cast<void*>(static_cast<const void*>(&(TOP.fc_layer__DOT__WEIGHT_WIDTH))), true, VLVT_UINT32,VLVD_NODIR|VLVF_PUB_RW,0,1 ,31,0);
        __Vscope_fc_layer.varInsert(__Vfinal,"accumulator", &(TOP.fc_layer__DOT__accumulator), false, VLVT_UINT64,VLVD_NODIR|VLVF_PUB_RW,0,1 ,41,0);
        __Vscope_fc_layer.varInsert(__Vfinal,"accumulator_next", &(TOP.fc_layer__DOT__accumulator_next), false, VLVT_UINT64,VLVD_NODIR|VLVF_PUB_RW,0,1 ,41,0);
        __Vscope_fc_layer.varInsert(__Vfinal,"bias_addr_i", &(TOP.fc_layer__DOT__bias_addr_i), false, VLVT_UINT16,VLVD_NODIR|VLVF_PUB_RW,0,1 ,9,0);
        __Vscope_fc_layer.varInsert(__Vfinal,"bias_data_i", &(TOP.fc_layer__DOT__bias_data_i), false, VLVT_UINT16,VLVD_NODIR|VLVF_PUB_RW,0,1 ,15,0);
        __Vscope_fc_layer.varInsert(__Vfinal,"bias_loading_done", &(TOP.fc_layer__DOT__bias_loading_done), false, VLVT_UINT8,VLVD_NODIR|VLVF_PUB_RW,0,0);
        __Vscope_fc_layer.varInsert(__Vfinal,"bias_memory", &(TOP.fc_layer__DOT__bias_memory), false, VLVT_WDATA,VLVD_NODIR|VLVF_PUB_RW,0,2 ,9,0 ,15,0);
        __Vscope_fc_layer.varInsert(__Vfinal,"bias_we_i", &(TOP.fc_layer__DOT__bias_we_i), false, VLVT_UINT8,VLVD_NODIR|VLVF_PUB_RW,0,0);
        __Vscope_fc_layer.varInsert(__Vfinal,"clk", &(TOP.fc_layer__DOT__clk), false, VLVT_UINT8,VLVD_NODIR|VLVF_PUB_RW,0,0);
        __Vscope_fc_layer.varInsert(__Vfinal,"computation_done", &(TOP.fc_layer__DOT__computation_done), false, VLVT_UINT8,VLVD_NODIR|VLVF_PUB_RW,0,0);
        __Vscope_fc_layer.varInsert(__Vfinal,"current_state", &(TOP.fc_layer__DOT__current_state), false, VLVT_UINT8,VLVD_NODIR|VLVF_PUB_RW,0,1 ,2,0);
        __Vscope_fc_layer.varInsert(__Vfinal,"debug_accumulator_o", &(TOP.fc_layer__DOT__debug_accumulator_o), false, VLVT_UINT16,VLVD_NODIR|VLVF_PUB_RW,0,1 ,15,0);
        __Vscope_fc_layer.varInsert(__Vfinal,"debug_addr_counter_o", &(TOP.fc_layer__DOT__debug_addr_counter_o), false, VLVT_UINT16,VLVD_NODIR|VLVF_PUB_RW,0,1 ,9,0);
        __Vscope_fc_layer.varInsert(__Vfinal,"debug_flags_o", &(TOP.fc_layer__DOT__debug_flags_o), false, VLVT_UINT8,VLVD_NODIR|VLVF_PUB_RW,0,1 ,3,0);
        __Vscope_fc_layer.varInsert(__Vfinal,"debug_state_o", &(TOP.fc_layer__DOT__debug_state_o), false, VLVT_UINT32,VLVD_NODIR|VLVF_PUB_RW,0,1 ,31,0);
        __Vscope_fc_layer.varInsert(__Vfinal,"final_result", &(TOP.fc_layer__DOT__final_result), false, VLVT_UINT16,VLVD_NODIR|VLVF_PUB_RW,0,1 ,15,0);
        __Vscope_fc_layer.varInsert(__Vfinal,"input_counter", &(TOP.fc_layer__DOT__input_counter), false, VLVT_UINT16,VLVD_NODIR|VLVF_PUB_RW,0,1 ,9,0);
        __Vscope_fc_layer.varInsert(__Vfinal,"input_counter_next", &(TOP.fc_layer__DOT__input_counter_next), false, VLVT_UINT16,VLVD_NODIR|VLVF_PUB_RW,0,1 ,9,0);
        __Vscope_fc_layer.varInsert(__Vfinal,"input_data_i", &(TOP.fc_layer__DOT__input_data_i), false, VLVT_WDATA,VLVD_NODIR|VLVF_PUB_RW,0,2 ,99,0 ,15,0);
        __Vscope_fc_layer.varInsert(__Vfinal,"input_reg", &(TOP.fc_layer__DOT__input_reg), false, VLVT_WDATA,VLVD_NODIR|VLVF_PUB_RW,0,2 ,99,0 ,15,0);
        __Vscope_fc_layer.varInsert(__Vfinal,"mode_i", &(TOP.fc_layer__DOT__mode_i), false, VLVT_UINT8,VLVD_NODIR|VLVF_PUB_RW,0,0);
        __Vscope_fc_layer.varInsert(__Vfinal,"mult_result", &(TOP.fc_layer__DOT__mult_result), false, VLVT_UINT16,VLVD_NODIR|VLVF_PUB_RW,0,1 ,15,0);
        __Vscope_fc_layer.varInsert(__Vfinal,"mult_result_full", &(TOP.fc_layer__DOT__mult_result_full), false, VLVT_UINT32,VLVD_NODIR|VLVF_PUB_RW,0,1 ,31,0);
        __Vscope_fc_layer.varInsert(__Vfinal,"next_state", &(TOP.fc_layer__DOT__next_state), false, VLVT_UINT8,VLVD_NODIR|VLVF_PUB_RW,0,1 ,2,0);
        __Vscope_fc_layer.varInsert(__Vfinal,"output_counter", &(TOP.fc_layer__DOT__output_counter), false, VLVT_UINT16,VLVD_NODIR|VLVF_PUB_RW,0,1 ,9,0);
        __Vscope_fc_layer.varInsert(__Vfinal,"output_counter_next", &(TOP.fc_layer__DOT__output_counter_next), false, VLVT_UINT16,VLVD_NODIR|VLVF_PUB_RW,0,1 ,9,0);
        __Vscope_fc_layer.varInsert(__Vfinal,"output_data_o", &(TOP.fc_layer__DOT__output_data_o), false, VLVT_WDATA,VLVD_NODIR|VLVF_PUB_RW,0,2 ,9,0 ,15,0);
        __Vscope_fc_layer.varInsert(__Vfinal,"output_reg", &(TOP.fc_layer__DOT__output_reg), false, VLVT_WDATA,VLVD_NODIR|VLVF_PUB_RW,0,2 ,9,0 ,15,0);
        __Vscope_fc_layer.varInsert(__Vfinal,"output_reg_next", &(TOP.fc_layer__DOT__output_reg_next), false, VLVT_WDATA,VLVD_NODIR|VLVF_PUB_RW,0,2 ,9,0 ,15,0);
        __Vscope_fc_layer.varInsert(__Vfinal,"overflow_flag", &(TOP.fc_layer__DOT__overflow_flag), false, VLVT_UINT8,VLVD_NODIR|VLVF_PUB_RW,0,0);
        __Vscope_fc_layer.varInsert(__Vfinal,"ready_o", &(TOP.fc_layer__DOT__ready_o), false, VLVT_UINT8,VLVD_NODIR|VLVF_PUB_RW,0,0);
        __Vscope_fc_layer.varInsert(__Vfinal,"rst_n", &(TOP.fc_layer__DOT__rst_n), false, VLVT_UINT8,VLVD_NODIR|VLVF_PUB_RW,0,0);
        __Vscope_fc_layer.varInsert(__Vfinal,"underflow_flag", &(TOP.fc_layer__DOT__underflow_flag), false, VLVT_UINT8,VLVD_NODIR|VLVF_PUB_RW,0,0);
        __Vscope_fc_layer.varInsert(__Vfinal,"valid_i", &(TOP.fc_layer__DOT__valid_i), false, VLVT_UINT8,VLVD_NODIR|VLVF_PUB_RW,0,0);
        __Vscope_fc_layer.varInsert(__Vfinal,"valid_o", &(TOP.fc_layer__DOT__valid_o), false, VLVT_UINT8,VLVD_NODIR|VLVF_PUB_RW,0,0);
        __Vscope_fc_layer.varInsert(__Vfinal,"weight_addr_i", &(TOP.fc_layer__DOT__weight_addr_i), false, VLVT_UINT16,VLVD_NODIR|VLVF_PUB_RW,0,1 ,9,0);
        __Vscope_fc_layer.varInsert(__Vfinal,"weight_data_i", &(TOP.fc_layer__DOT__weight_data_i), false, VLVT_UINT16,VLVD_NODIR|VLVF_PUB_RW,0,1 ,15,0);
        __Vscope_fc_layer.varInsert(__Vfinal,"weight_loading_done", &(TOP.fc_layer__DOT__weight_loading_done), false, VLVT_UINT8,VLVD_NODIR|VLVF_PUB_RW,0,0);
        __Vscope_fc_layer.varInsert(__Vfinal,"weight_memory", &(TOP.fc_layer__DOT__weight_memory), false, VLVT_WDATA,VLVD_NODIR|VLVF_PUB_RW,0,3 ,99,0 ,9,0 ,15,0);
        __Vscope_fc_layer.varInsert(__Vfinal,"weight_we_i", &(TOP.fc_layer__DOT__weight_we_i), false, VLVT_UINT8,VLVD_NODIR|VLVF_PUB_RW,0,0);
        __Vscope_fc_layer__unnamedblk1.varInsert(__Vfinal,"i", &(TOP.fc_layer__DOT__unnamedblk1__DOT__i), false, VLVT_UINT32,VLVD_NODIR|VLVF_PUB_RW|VLVF_DPI_CLAY,0,1 ,31,0);
        __Vscope_fc_layer__unnamedblk1__unnamedblk2.varInsert(__Vfinal,"j", &(TOP.fc_layer__DOT__unnamedblk1__DOT__unnamedblk2__DOT__j), false, VLVT_UINT32,VLVD_NODIR|VLVF_PUB_RW|VLVF_DPI_CLAY,0,1 ,31,0);
        __Vscope_fc_layer__unnamedblk3.varInsert(__Vfinal,"j", &(TOP.fc_layer__DOT__unnamedblk3__DOT__j), false, VLVT_UINT32,VLVD_NODIR|VLVF_PUB_RW|VLVF_DPI_CLAY,0,1 ,31,0);
        __Vscope_fc_layer__unnamedblk4.varInsert(__Vfinal,"input_idx", &(TOP.fc_layer__DOT__unnamedblk4__DOT__input_idx), false, VLVT_UINT8,VLVD_NODIR|VLVF_PUB_RW,0,1 ,6,0);
        __Vscope_fc_layer__unnamedblk4.varInsert(__Vfinal,"output_idx", &(TOP.fc_layer__DOT__unnamedblk4__DOT__output_idx), false, VLVT_UINT8,VLVD_NODIR|VLVF_PUB_RW,0,1 ,3,0);
    }
}
