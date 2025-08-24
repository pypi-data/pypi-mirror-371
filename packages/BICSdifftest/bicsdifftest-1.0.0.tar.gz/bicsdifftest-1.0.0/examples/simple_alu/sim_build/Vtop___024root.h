// Verilated -*- C++ -*-
// DESCRIPTION: Verilator output: Design internal header
// See Vtop.h for the primary calling header

#ifndef VERILATED_VTOP___024ROOT_H_
#define VERILATED_VTOP___024ROOT_H_  // guard

#include "verilated.h"


class Vtop__Syms;

class alignas(VL_CACHE_LINE_BYTES) Vtop___024root final : public VerilatedModule {
  public:

    // DESIGN SPECIFIC STATE
    VL_IN8(clk,0,0);
    VL_IN8(rst_n,0,0);
    VL_IN8(valid_i,0,0);
    VL_OUT8(ready_o,0,0);
    VL_IN8(op_i,3,0);
    VL_OUT8(valid_o,0,0);
    VL_OUT8(overflow_o,0,0);
    VL_OUT8(zero_o,0,0);
    VL_OUT8(debug_flags_o,3,0);
    CData/*0:0*/ simple_alu__DOT__clk;
    CData/*0:0*/ simple_alu__DOT__rst_n;
    CData/*0:0*/ simple_alu__DOT__valid_i;
    CData/*0:0*/ simple_alu__DOT__ready_o;
    CData/*3:0*/ simple_alu__DOT__op_i;
    CData/*0:0*/ simple_alu__DOT__valid_o;
    CData/*0:0*/ simple_alu__DOT__overflow_o;
    CData/*0:0*/ simple_alu__DOT__zero_o;
    CData/*3:0*/ simple_alu__DOT__debug_flags_o;
    CData/*3:0*/ simple_alu__DOT__operation_reg;
    CData/*0:0*/ simple_alu__DOT__input_valid_reg;
    CData/*0:0*/ simple_alu__DOT__stage1_overflow;
    CData/*0:0*/ simple_alu__DOT__stage2_overflow;
    CData/*0:0*/ simple_alu__DOT__final_overflow;
    CData/*0:0*/ simple_alu__DOT__computation_valid;
    CData/*1:0*/ simple_alu__DOT__pipeline_counter;
    CData/*5:0*/ simple_alu__DOT__shift_amount;
    CData/*5:0*/ simple_alu__DOT__rotate_amount;
    CData/*0:0*/ __VstlFirstIteration;
    CData/*0:0*/ __VicoFirstIteration;
    CData/*0:0*/ __Vtrigprevexpr___TOP__clk__0;
    CData/*0:0*/ __Vtrigprevexpr___TOP__rst_n__0;
    CData/*0:0*/ __VactContinue;
    VL_IN(a_i,31,0);
    VL_IN(b_i,31,0);
    VL_OUT(result_o,31,0);
    VL_OUT(debug_stage1_o,31,0);
    VL_OUT(debug_stage2_o,31,0);
    IData/*31:0*/ simple_alu__DOT__a_i;
    IData/*31:0*/ simple_alu__DOT__b_i;
    IData/*31:0*/ simple_alu__DOT__result_o;
    IData/*31:0*/ simple_alu__DOT__debug_stage1_o;
    IData/*31:0*/ simple_alu__DOT__debug_stage2_o;
    IData/*31:0*/ simple_alu__DOT__operand_a_reg;
    IData/*31:0*/ simple_alu__DOT__operand_b_reg;
    IData/*31:0*/ simple_alu__DOT__stage1_result;
    IData/*31:0*/ simple_alu__DOT__stage2_result;
    IData/*31:0*/ simple_alu__DOT__final_result;
    IData/*31:0*/ __VactIterCount;
    QData/*63:0*/ simple_alu__DOT__mul_result;
    VlTriggerVec<1> __VstlTriggered;
    VlTriggerVec<1> __VicoTriggered;
    VlTriggerVec<2> __VactTriggered;
    VlTriggerVec<2> __VnbaTriggered;

    // INTERNAL VARIABLES
    Vtop__Syms* const vlSymsp;

    // PARAMETERS
    static constexpr IData/*31:0*/ simple_alu__DOT__DATA_WIDTH = 0x00000020U;
    static constexpr IData/*31:0*/ simple_alu__DOT__OP_WIDTH = 4U;

    // CONSTRUCTORS
    Vtop___024root(Vtop__Syms* symsp, const char* v__name);
    ~Vtop___024root();
    VL_UNCOPYABLE(Vtop___024root);

    // INTERNAL METHODS
    void __Vconfigure(bool first);
};


#endif  // guard
