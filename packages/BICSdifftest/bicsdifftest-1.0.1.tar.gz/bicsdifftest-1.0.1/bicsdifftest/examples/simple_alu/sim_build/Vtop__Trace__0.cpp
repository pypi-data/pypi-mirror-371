// Verilated -*- C++ -*-
// DESCRIPTION: Verilator output: Tracing implementation internals
#include "verilated_fst_c.h"
#include "Vtop__Syms.h"


void Vtop___024root__trace_chg_0_sub_0(Vtop___024root* vlSelf, VerilatedFst::Buffer* bufp);

void Vtop___024root__trace_chg_0(void* voidSelf, VerilatedFst::Buffer* bufp) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtop___024root__trace_chg_0\n"); );
    // Init
    Vtop___024root* const __restrict vlSelf VL_ATTR_UNUSED = static_cast<Vtop___024root*>(voidSelf);
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    if (VL_UNLIKELY(!vlSymsp->__Vm_activity)) return;
    // Body
    Vtop___024root__trace_chg_0_sub_0((&vlSymsp->TOP), bufp);
}

void Vtop___024root__trace_chg_0_sub_0(Vtop___024root* vlSelf, VerilatedFst::Buffer* bufp) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtop___024root__trace_chg_0_sub_0\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Init
    uint32_t* const oldp VL_ATTR_UNUSED = bufp->oldp(vlSymsp->__Vm_baseCode + 1);
    // Body
    bufp->chgBit(oldp+0,(vlSelfRef.clk));
    bufp->chgBit(oldp+1,(vlSelfRef.rst_n));
    bufp->chgBit(oldp+2,(vlSelfRef.valid_i));
    bufp->chgBit(oldp+3,(vlSelfRef.ready_o));
    bufp->chgIData(oldp+4,(vlSelfRef.a_i),32);
    bufp->chgIData(oldp+5,(vlSelfRef.b_i),32);
    bufp->chgCData(oldp+6,(vlSelfRef.op_i),4);
    bufp->chgIData(oldp+7,(vlSelfRef.result_o),32);
    bufp->chgBit(oldp+8,(vlSelfRef.valid_o));
    bufp->chgBit(oldp+9,(vlSelfRef.overflow_o));
    bufp->chgBit(oldp+10,(vlSelfRef.zero_o));
    bufp->chgIData(oldp+11,(vlSelfRef.debug_stage1_o),32);
    bufp->chgIData(oldp+12,(vlSelfRef.debug_stage2_o),32);
    bufp->chgCData(oldp+13,(vlSelfRef.debug_flags_o),4);
    bufp->chgBit(oldp+14,(vlSelfRef.simple_alu__DOT__clk));
    bufp->chgBit(oldp+15,(vlSelfRef.simple_alu__DOT__rst_n));
    bufp->chgBit(oldp+16,(vlSelfRef.simple_alu__DOT__valid_i));
    bufp->chgBit(oldp+17,(vlSelfRef.simple_alu__DOT__ready_o));
    bufp->chgIData(oldp+18,(vlSelfRef.simple_alu__DOT__a_i),32);
    bufp->chgIData(oldp+19,(vlSelfRef.simple_alu__DOT__b_i),32);
    bufp->chgCData(oldp+20,(vlSelfRef.simple_alu__DOT__op_i),4);
    bufp->chgIData(oldp+21,(vlSelfRef.simple_alu__DOT__result_o),32);
    bufp->chgBit(oldp+22,(vlSelfRef.simple_alu__DOT__valid_o));
    bufp->chgBit(oldp+23,(vlSelfRef.simple_alu__DOT__overflow_o));
    bufp->chgBit(oldp+24,(vlSelfRef.simple_alu__DOT__zero_o));
    bufp->chgIData(oldp+25,(vlSelfRef.simple_alu__DOT__debug_stage1_o),32);
    bufp->chgIData(oldp+26,(vlSelfRef.simple_alu__DOT__debug_stage2_o),32);
    bufp->chgCData(oldp+27,(vlSelfRef.simple_alu__DOT__debug_flags_o),4);
    bufp->chgIData(oldp+28,(vlSelfRef.simple_alu__DOT__operand_a_reg),32);
    bufp->chgIData(oldp+29,(vlSelfRef.simple_alu__DOT__operand_b_reg),32);
    bufp->chgCData(oldp+30,(vlSelfRef.simple_alu__DOT__operation_reg),4);
    bufp->chgBit(oldp+31,(vlSelfRef.simple_alu__DOT__input_valid_reg));
    bufp->chgIData(oldp+32,(vlSelfRef.simple_alu__DOT__stage1_result),32);
    bufp->chgIData(oldp+33,(vlSelfRef.simple_alu__DOT__stage2_result),32);
    bufp->chgIData(oldp+34,(vlSelfRef.simple_alu__DOT__final_result),32);
    bufp->chgBit(oldp+35,(vlSelfRef.simple_alu__DOT__stage1_overflow));
    bufp->chgBit(oldp+36,(vlSelfRef.simple_alu__DOT__stage2_overflow));
    bufp->chgBit(oldp+37,(vlSelfRef.simple_alu__DOT__final_overflow));
    bufp->chgBit(oldp+38,(vlSelfRef.simple_alu__DOT__computation_valid));
    bufp->chgCData(oldp+39,(vlSelfRef.simple_alu__DOT__pipeline_counter),2);
    bufp->chgQData(oldp+40,(vlSelfRef.simple_alu__DOT__mul_result),64);
    bufp->chgCData(oldp+42,(vlSelfRef.simple_alu__DOT__shift_amount),6);
    bufp->chgCData(oldp+43,(vlSelfRef.simple_alu__DOT__rotate_amount),6);
}

void Vtop___024root__trace_cleanup(void* voidSelf, VerilatedFst* /*unused*/) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtop___024root__trace_cleanup\n"); );
    // Init
    Vtop___024root* const __restrict vlSelf VL_ATTR_UNUSED = static_cast<Vtop___024root*>(voidSelf);
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    VlUnpacked<CData/*0:0*/, 1> __Vm_traceActivity;
    for (int __Vi0 = 0; __Vi0 < 1; ++__Vi0) {
        __Vm_traceActivity[__Vi0] = 0;
    }
    // Body
    vlSymsp->__Vm_activity = false;
    __Vm_traceActivity[0U] = 0U;
}
