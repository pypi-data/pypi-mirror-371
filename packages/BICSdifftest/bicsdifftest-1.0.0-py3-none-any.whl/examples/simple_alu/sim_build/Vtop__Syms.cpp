// Verilated -*- C++ -*-
// DESCRIPTION: Verilator output: Symbol table implementation internals

#include "Vtop__pch.h"
#include "Vtop.h"
#include "Vtop___024root.h"

// FUNCTIONS
Vtop__Syms::~Vtop__Syms()
{

    // Tear down scope hierarchy
    __Vhier.remove(0, &__Vscope_simple_alu);

}

Vtop__Syms::Vtop__Syms(VerilatedContext* contextp, const char* namep, Vtop* modelp)
    : VerilatedSyms{contextp}
    // Setup internal state of the Syms class
    , __Vm_modelp{modelp}
    // Setup module instances
    , TOP{this, namep}
{
        // Check resources
        Verilated::stackCheck(25);
    // Configure time unit / time precision
    _vm_contextp__->timeunit(-9);
    _vm_contextp__->timeprecision(-12);
    // Setup each module's pointers to their submodules
    // Setup each module's pointer back to symbol table (for public functions)
    TOP.__Vconfigure(true);
    // Setup scopes
    __Vscope_TOP.configure(this, name(), "TOP", "TOP", "<null>", 0, VerilatedScope::SCOPE_OTHER);
    __Vscope_simple_alu.configure(this, name(), "simple_alu", "simple_alu", "simple_alu", -9, VerilatedScope::SCOPE_MODULE);

    // Set up scope hierarchy
    __Vhier.add(0, &__Vscope_simple_alu);

    // Setup export functions
    for (int __Vfinal = 0; __Vfinal < 2; ++__Vfinal) {
        __Vscope_TOP.varInsert(__Vfinal,"a_i", &(TOP.a_i), false, VLVT_UINT32,VLVD_IN|VLVF_PUB_RW,0,1 ,31,0);
        __Vscope_TOP.varInsert(__Vfinal,"b_i", &(TOP.b_i), false, VLVT_UINT32,VLVD_IN|VLVF_PUB_RW,0,1 ,31,0);
        __Vscope_TOP.varInsert(__Vfinal,"clk", &(TOP.clk), false, VLVT_UINT8,VLVD_IN|VLVF_PUB_RW,0,0);
        __Vscope_TOP.varInsert(__Vfinal,"debug_flags_o", &(TOP.debug_flags_o), false, VLVT_UINT8,VLVD_OUT|VLVF_PUB_RW,0,1 ,3,0);
        __Vscope_TOP.varInsert(__Vfinal,"debug_stage1_o", &(TOP.debug_stage1_o), false, VLVT_UINT32,VLVD_OUT|VLVF_PUB_RW,0,1 ,31,0);
        __Vscope_TOP.varInsert(__Vfinal,"debug_stage2_o", &(TOP.debug_stage2_o), false, VLVT_UINT32,VLVD_OUT|VLVF_PUB_RW,0,1 ,31,0);
        __Vscope_TOP.varInsert(__Vfinal,"op_i", &(TOP.op_i), false, VLVT_UINT8,VLVD_IN|VLVF_PUB_RW,0,1 ,3,0);
        __Vscope_TOP.varInsert(__Vfinal,"overflow_o", &(TOP.overflow_o), false, VLVT_UINT8,VLVD_OUT|VLVF_PUB_RW,0,0);
        __Vscope_TOP.varInsert(__Vfinal,"ready_o", &(TOP.ready_o), false, VLVT_UINT8,VLVD_OUT|VLVF_PUB_RW,0,0);
        __Vscope_TOP.varInsert(__Vfinal,"result_o", &(TOP.result_o), false, VLVT_UINT32,VLVD_OUT|VLVF_PUB_RW,0,1 ,31,0);
        __Vscope_TOP.varInsert(__Vfinal,"rst_n", &(TOP.rst_n), false, VLVT_UINT8,VLVD_IN|VLVF_PUB_RW,0,0);
        __Vscope_TOP.varInsert(__Vfinal,"valid_i", &(TOP.valid_i), false, VLVT_UINT8,VLVD_IN|VLVF_PUB_RW,0,0);
        __Vscope_TOP.varInsert(__Vfinal,"valid_o", &(TOP.valid_o), false, VLVT_UINT8,VLVD_OUT|VLVF_PUB_RW,0,0);
        __Vscope_TOP.varInsert(__Vfinal,"zero_o", &(TOP.zero_o), false, VLVT_UINT8,VLVD_OUT|VLVF_PUB_RW,0,0);
        __Vscope_simple_alu.varInsert(__Vfinal,"DATA_WIDTH", const_cast<void*>(static_cast<const void*>(&(TOP.simple_alu__DOT__DATA_WIDTH))), true, VLVT_UINT32,VLVD_NODIR|VLVF_PUB_RW,0,1 ,31,0);
        __Vscope_simple_alu.varInsert(__Vfinal,"OP_WIDTH", const_cast<void*>(static_cast<const void*>(&(TOP.simple_alu__DOT__OP_WIDTH))), true, VLVT_UINT32,VLVD_NODIR|VLVF_PUB_RW,0,1 ,31,0);
        __Vscope_simple_alu.varInsert(__Vfinal,"a_i", &(TOP.simple_alu__DOT__a_i), false, VLVT_UINT32,VLVD_NODIR|VLVF_PUB_RW,0,1 ,31,0);
        __Vscope_simple_alu.varInsert(__Vfinal,"b_i", &(TOP.simple_alu__DOT__b_i), false, VLVT_UINT32,VLVD_NODIR|VLVF_PUB_RW,0,1 ,31,0);
        __Vscope_simple_alu.varInsert(__Vfinal,"clk", &(TOP.simple_alu__DOT__clk), false, VLVT_UINT8,VLVD_NODIR|VLVF_PUB_RW,0,0);
        __Vscope_simple_alu.varInsert(__Vfinal,"computation_valid", &(TOP.simple_alu__DOT__computation_valid), false, VLVT_UINT8,VLVD_NODIR|VLVF_PUB_RW,0,0);
        __Vscope_simple_alu.varInsert(__Vfinal,"debug_flags_o", &(TOP.simple_alu__DOT__debug_flags_o), false, VLVT_UINT8,VLVD_NODIR|VLVF_PUB_RW,0,1 ,3,0);
        __Vscope_simple_alu.varInsert(__Vfinal,"debug_stage1_o", &(TOP.simple_alu__DOT__debug_stage1_o), false, VLVT_UINT32,VLVD_NODIR|VLVF_PUB_RW,0,1 ,31,0);
        __Vscope_simple_alu.varInsert(__Vfinal,"debug_stage2_o", &(TOP.simple_alu__DOT__debug_stage2_o), false, VLVT_UINT32,VLVD_NODIR|VLVF_PUB_RW,0,1 ,31,0);
        __Vscope_simple_alu.varInsert(__Vfinal,"final_overflow", &(TOP.simple_alu__DOT__final_overflow), false, VLVT_UINT8,VLVD_NODIR|VLVF_PUB_RW,0,0);
        __Vscope_simple_alu.varInsert(__Vfinal,"final_result", &(TOP.simple_alu__DOT__final_result), false, VLVT_UINT32,VLVD_NODIR|VLVF_PUB_RW,0,1 ,31,0);
        __Vscope_simple_alu.varInsert(__Vfinal,"input_valid_reg", &(TOP.simple_alu__DOT__input_valid_reg), false, VLVT_UINT8,VLVD_NODIR|VLVF_PUB_RW,0,0);
        __Vscope_simple_alu.varInsert(__Vfinal,"mul_result", &(TOP.simple_alu__DOT__mul_result), false, VLVT_UINT64,VLVD_NODIR|VLVF_PUB_RW,0,1 ,63,0);
        __Vscope_simple_alu.varInsert(__Vfinal,"op_i", &(TOP.simple_alu__DOT__op_i), false, VLVT_UINT8,VLVD_NODIR|VLVF_PUB_RW,0,1 ,3,0);
        __Vscope_simple_alu.varInsert(__Vfinal,"operand_a_reg", &(TOP.simple_alu__DOT__operand_a_reg), false, VLVT_UINT32,VLVD_NODIR|VLVF_PUB_RW,0,1 ,31,0);
        __Vscope_simple_alu.varInsert(__Vfinal,"operand_b_reg", &(TOP.simple_alu__DOT__operand_b_reg), false, VLVT_UINT32,VLVD_NODIR|VLVF_PUB_RW,0,1 ,31,0);
        __Vscope_simple_alu.varInsert(__Vfinal,"operation_reg", &(TOP.simple_alu__DOT__operation_reg), false, VLVT_UINT8,VLVD_NODIR|VLVF_PUB_RW,0,1 ,3,0);
        __Vscope_simple_alu.varInsert(__Vfinal,"overflow_o", &(TOP.simple_alu__DOT__overflow_o), false, VLVT_UINT8,VLVD_NODIR|VLVF_PUB_RW,0,0);
        __Vscope_simple_alu.varInsert(__Vfinal,"pipeline_counter", &(TOP.simple_alu__DOT__pipeline_counter), false, VLVT_UINT8,VLVD_NODIR|VLVF_PUB_RW,0,1 ,1,0);
        __Vscope_simple_alu.varInsert(__Vfinal,"ready_o", &(TOP.simple_alu__DOT__ready_o), false, VLVT_UINT8,VLVD_NODIR|VLVF_PUB_RW,0,0);
        __Vscope_simple_alu.varInsert(__Vfinal,"result_o", &(TOP.simple_alu__DOT__result_o), false, VLVT_UINT32,VLVD_NODIR|VLVF_PUB_RW,0,1 ,31,0);
        __Vscope_simple_alu.varInsert(__Vfinal,"rotate_amount", &(TOP.simple_alu__DOT__rotate_amount), false, VLVT_UINT8,VLVD_NODIR|VLVF_PUB_RW,0,1 ,5,0);
        __Vscope_simple_alu.varInsert(__Vfinal,"rst_n", &(TOP.simple_alu__DOT__rst_n), false, VLVT_UINT8,VLVD_NODIR|VLVF_PUB_RW,0,0);
        __Vscope_simple_alu.varInsert(__Vfinal,"shift_amount", &(TOP.simple_alu__DOT__shift_amount), false, VLVT_UINT8,VLVD_NODIR|VLVF_PUB_RW,0,1 ,5,0);
        __Vscope_simple_alu.varInsert(__Vfinal,"stage1_overflow", &(TOP.simple_alu__DOT__stage1_overflow), false, VLVT_UINT8,VLVD_NODIR|VLVF_PUB_RW,0,0);
        __Vscope_simple_alu.varInsert(__Vfinal,"stage1_result", &(TOP.simple_alu__DOT__stage1_result), false, VLVT_UINT32,VLVD_NODIR|VLVF_PUB_RW,0,1 ,31,0);
        __Vscope_simple_alu.varInsert(__Vfinal,"stage2_overflow", &(TOP.simple_alu__DOT__stage2_overflow), false, VLVT_UINT8,VLVD_NODIR|VLVF_PUB_RW,0,0);
        __Vscope_simple_alu.varInsert(__Vfinal,"stage2_result", &(TOP.simple_alu__DOT__stage2_result), false, VLVT_UINT32,VLVD_NODIR|VLVF_PUB_RW,0,1 ,31,0);
        __Vscope_simple_alu.varInsert(__Vfinal,"valid_i", &(TOP.simple_alu__DOT__valid_i), false, VLVT_UINT8,VLVD_NODIR|VLVF_PUB_RW,0,0);
        __Vscope_simple_alu.varInsert(__Vfinal,"valid_o", &(TOP.simple_alu__DOT__valid_o), false, VLVT_UINT8,VLVD_NODIR|VLVF_PUB_RW,0,0);
        __Vscope_simple_alu.varInsert(__Vfinal,"zero_o", &(TOP.simple_alu__DOT__zero_o), false, VLVT_UINT8,VLVD_NODIR|VLVF_PUB_RW,0,0);
    }
}
