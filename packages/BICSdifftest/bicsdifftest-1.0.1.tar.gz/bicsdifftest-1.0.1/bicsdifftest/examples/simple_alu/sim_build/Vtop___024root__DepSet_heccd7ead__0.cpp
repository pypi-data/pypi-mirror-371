// Verilated -*- C++ -*-
// DESCRIPTION: Verilator output: Design implementation internals
// See Vtop.h for the primary calling header

#include "Vtop__pch.h"
#include "Vtop___024root.h"

void Vtop___024root___ico_sequent__TOP__0(Vtop___024root* vlSelf);

void Vtop___024root___eval_ico(Vtop___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtop___024root___eval_ico\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    if ((1ULL & vlSelfRef.__VicoTriggered.word(0U))) {
        Vtop___024root___ico_sequent__TOP__0(vlSelf);
    }
}

VL_INLINE_OPT void Vtop___024root___ico_sequent__TOP__0(Vtop___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtop___024root___ico_sequent__TOP__0\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.simple_alu__DOT__clk = vlSelfRef.clk;
    vlSelfRef.simple_alu__DOT__rst_n = vlSelfRef.rst_n;
    vlSelfRef.simple_alu__DOT__valid_i = vlSelfRef.valid_i;
    vlSelfRef.simple_alu__DOT__a_i = vlSelfRef.a_i;
    vlSelfRef.simple_alu__DOT__b_i = vlSelfRef.b_i;
    vlSelfRef.simple_alu__DOT__op_i = vlSelfRef.op_i;
    vlSelfRef.result_o = vlSelfRef.simple_alu__DOT__final_result;
    vlSelfRef.overflow_o = vlSelfRef.simple_alu__DOT__final_overflow;
    vlSelfRef.simple_alu__DOT__result_o = vlSelfRef.simple_alu__DOT__final_result;
    vlSelfRef.simple_alu__DOT__overflow_o = vlSelfRef.simple_alu__DOT__final_overflow;
    vlSelfRef.valid_o = vlSelfRef.simple_alu__DOT__valid_o;
    vlSelfRef.simple_alu__DOT__ready_o = (1U & (~ (IData)(vlSelfRef.simple_alu__DOT__input_valid_reg)));
    vlSelfRef.simple_alu__DOT__computation_valid = 
        ((3U == (IData)(vlSelfRef.simple_alu__DOT__pipeline_counter)) 
         | ((2U != (IData)(vlSelfRef.simple_alu__DOT__operation_reg)) 
            & ((3U != (IData)(vlSelfRef.simple_alu__DOT__operation_reg)) 
               & (IData)(vlSelfRef.simple_alu__DOT__input_valid_reg))));
    vlSelfRef.simple_alu__DOT__zero_o = (0U == vlSelfRef.simple_alu__DOT__final_result);
    vlSelfRef.simple_alu__DOT__stage1_result = 0U;
    vlSelfRef.simple_alu__DOT__stage1_overflow = 0U;
    vlSelfRef.simple_alu__DOT__mul_result = 0ULL;
    vlSelfRef.ready_o = vlSelfRef.simple_alu__DOT__ready_o;
    vlSelfRef.zero_o = vlSelfRef.simple_alu__DOT__zero_o;
    vlSelfRef.debug_flags_o = ((((IData)(vlSelfRef.simple_alu__DOT__final_overflow) 
                                 << 3U) | ((IData)(vlSelfRef.simple_alu__DOT__zero_o) 
                                           << 2U)) 
                               | (((IData)(vlSelfRef.simple_alu__DOT__computation_valid) 
                                   << 1U) | (IData)(vlSelfRef.simple_alu__DOT__input_valid_reg)));
    if ((8U & (IData)(vlSelfRef.simple_alu__DOT__operation_reg))) {
        vlSelfRef.simple_alu__DOT__stage1_result = vlSelfRef.simple_alu__DOT__operand_a_reg;
        vlSelfRef.debug_stage1_o = vlSelfRef.simple_alu__DOT__stage1_result;
        vlSelfRef.simple_alu__DOT__debug_stage1_o = vlSelfRef.simple_alu__DOT__stage1_result;
        vlSelfRef.simple_alu__DOT__stage2_result = vlSelfRef.simple_alu__DOT__stage1_result;
        vlSelfRef.simple_alu__DOT__stage2_overflow 
            = vlSelfRef.simple_alu__DOT__stage1_overflow;
        vlSelfRef.simple_alu__DOT__shift_amount = 0U;
        vlSelfRef.simple_alu__DOT__rotate_amount = 0U;
        if ((4U & (IData)(vlSelfRef.simple_alu__DOT__operation_reg))) {
            vlSelfRef.simple_alu__DOT__stage2_result 
                = ((2U & (IData)(vlSelfRef.simple_alu__DOT__operation_reg))
                    ? ((1U & (IData)(vlSelfRef.simple_alu__DOT__operation_reg))
                        ? vlSelfRef.simple_alu__DOT__stage1_result
                        : ((vlSelfRef.simple_alu__DOT__operand_a_reg 
                            == vlSelfRef.simple_alu__DOT__operand_b_reg)
                            ? 0U : ((vlSelfRef.simple_alu__DOT__operand_a_reg 
                                     > vlSelfRef.simple_alu__DOT__operand_b_reg)
                                     ? 1U : 0xffffffffU)))
                    : ((1U & (IData)(vlSelfRef.simple_alu__DOT__operation_reg))
                        ? ((vlSelfRef.simple_alu__DOT__operand_a_reg 
                            < vlSelfRef.simple_alu__DOT__operand_b_reg)
                            ? vlSelfRef.simple_alu__DOT__operand_a_reg
                            : vlSelfRef.simple_alu__DOT__operand_b_reg)
                        : ((vlSelfRef.simple_alu__DOT__operand_a_reg 
                            > vlSelfRef.simple_alu__DOT__operand_b_reg)
                            ? vlSelfRef.simple_alu__DOT__operand_a_reg
                            : vlSelfRef.simple_alu__DOT__operand_b_reg)));
        } else if ((2U & (IData)(vlSelfRef.simple_alu__DOT__operation_reg))) {
            if ((1U & (IData)(vlSelfRef.simple_alu__DOT__operation_reg))) {
                vlSelfRef.simple_alu__DOT__rotate_amount 
                    = (0x1fU & vlSelfRef.simple_alu__DOT__operand_b_reg);
                vlSelfRef.simple_alu__DOT__stage2_result 
                    = (VL_SHIFTR_III(32,32,6, vlSelfRef.simple_alu__DOT__stage1_result, (IData)(vlSelfRef.simple_alu__DOT__rotate_amount)) 
                       | VL_SHIFTL_III(32,32,32, vlSelfRef.simple_alu__DOT__stage1_result, 
                                       ((IData)(0x20U) 
                                        - (IData)(vlSelfRef.simple_alu__DOT__rotate_amount))));
            } else {
                vlSelfRef.simple_alu__DOT__rotate_amount 
                    = (0x1fU & vlSelfRef.simple_alu__DOT__operand_b_reg);
                vlSelfRef.simple_alu__DOT__stage2_result 
                    = (VL_SHIFTL_III(32,32,6, vlSelfRef.simple_alu__DOT__stage1_result, (IData)(vlSelfRef.simple_alu__DOT__rotate_amount)) 
                       | VL_SHIFTR_III(32,32,32, vlSelfRef.simple_alu__DOT__stage1_result, 
                                       ((IData)(0x20U) 
                                        - (IData)(vlSelfRef.simple_alu__DOT__rotate_amount))));
            }
        } else if ((1U & (IData)(vlSelfRef.simple_alu__DOT__operation_reg))) {
            vlSelfRef.simple_alu__DOT__shift_amount 
                = (0x3fU & vlSelfRef.simple_alu__DOT__operand_b_reg);
            vlSelfRef.simple_alu__DOT__stage2_result 
                = ((0x20U > (IData)(vlSelfRef.simple_alu__DOT__shift_amount))
                    ? VL_SHIFTR_III(32,32,6, vlSelfRef.simple_alu__DOT__stage1_result, (IData)(vlSelfRef.simple_alu__DOT__shift_amount))
                    : 0U);
        } else {
            vlSelfRef.simple_alu__DOT__shift_amount 
                = (0x3fU & vlSelfRef.simple_alu__DOT__operand_b_reg);
            if ((0x20U > (IData)(vlSelfRef.simple_alu__DOT__shift_amount))) {
                vlSelfRef.simple_alu__DOT__stage2_result 
                    = VL_SHIFTL_III(32,32,6, vlSelfRef.simple_alu__DOT__stage1_result, (IData)(vlSelfRef.simple_alu__DOT__shift_amount));
                vlSelfRef.simple_alu__DOT__stage2_overflow 
                    = (0U != VL_SHIFTR_III(32,32,32, vlSelfRef.simple_alu__DOT__stage1_result, 
                                           ((IData)(0x20U) 
                                            - (IData)(vlSelfRef.simple_alu__DOT__shift_amount))));
            } else {
                vlSelfRef.simple_alu__DOT__stage2_result = 0U;
                vlSelfRef.simple_alu__DOT__stage2_overflow 
                    = (0U != vlSelfRef.simple_alu__DOT__stage1_result);
            }
        }
    } else {
        if ((4U & (IData)(vlSelfRef.simple_alu__DOT__operation_reg))) {
            vlSelfRef.simple_alu__DOT__stage1_result 
                = ((2U & (IData)(vlSelfRef.simple_alu__DOT__operation_reg))
                    ? ((1U & (IData)(vlSelfRef.simple_alu__DOT__operation_reg))
                        ? (~ vlSelfRef.simple_alu__DOT__operand_a_reg)
                        : (vlSelfRef.simple_alu__DOT__operand_a_reg 
                           ^ vlSelfRef.simple_alu__DOT__operand_b_reg))
                    : ((1U & (IData)(vlSelfRef.simple_alu__DOT__operation_reg))
                        ? (vlSelfRef.simple_alu__DOT__operand_a_reg 
                           | vlSelfRef.simple_alu__DOT__operand_b_reg)
                        : (vlSelfRef.simple_alu__DOT__operand_a_reg 
                           & vlSelfRef.simple_alu__DOT__operand_b_reg)));
        } else if ((2U & (IData)(vlSelfRef.simple_alu__DOT__operation_reg))) {
            if ((1U & (IData)(vlSelfRef.simple_alu__DOT__operation_reg))) {
                if ((0U != vlSelfRef.simple_alu__DOT__operand_b_reg)) {
                    vlSelfRef.simple_alu__DOT__stage1_result 
                        = VL_DIV_III(32, vlSelfRef.simple_alu__DOT__operand_a_reg, vlSelfRef.simple_alu__DOT__operand_b_reg);
                    vlSelfRef.simple_alu__DOT__stage1_overflow = 0U;
                } else {
                    vlSelfRef.simple_alu__DOT__stage1_result = 0xffffffffU;
                    vlSelfRef.simple_alu__DOT__stage1_overflow = 1U;
                }
            } else {
                vlSelfRef.simple_alu__DOT__mul_result 
                    = ((QData)((IData)(vlSelfRef.simple_alu__DOT__operand_a_reg)) 
                       * (QData)((IData)(vlSelfRef.simple_alu__DOT__operand_b_reg)));
                vlSelfRef.simple_alu__DOT__stage1_result 
                    = (IData)(vlSelfRef.simple_alu__DOT__mul_result);
                vlSelfRef.simple_alu__DOT__stage1_overflow 
                    = (0U != (IData)((vlSelfRef.simple_alu__DOT__mul_result 
                                      >> 0x20U)));
            }
        } else if ((1U & (IData)(vlSelfRef.simple_alu__DOT__operation_reg))) {
            vlSelfRef.simple_alu__DOT__stage1_overflow 
                = (1U & (IData)((1ULL & (((QData)((IData)(vlSelfRef.simple_alu__DOT__operand_a_reg)) 
                                          - (QData)((IData)(vlSelfRef.simple_alu__DOT__operand_b_reg))) 
                                         >> 0x20U))));
            vlSelfRef.simple_alu__DOT__stage1_result 
                = (vlSelfRef.simple_alu__DOT__operand_a_reg 
                   - vlSelfRef.simple_alu__DOT__operand_b_reg);
        } else {
            vlSelfRef.simple_alu__DOT__stage1_overflow 
                = (1U & (IData)((1ULL & (((QData)((IData)(vlSelfRef.simple_alu__DOT__operand_a_reg)) 
                                          + (QData)((IData)(vlSelfRef.simple_alu__DOT__operand_b_reg))) 
                                         >> 0x20U))));
            vlSelfRef.simple_alu__DOT__stage1_result 
                = (vlSelfRef.simple_alu__DOT__operand_a_reg 
                   + vlSelfRef.simple_alu__DOT__operand_b_reg);
        }
        vlSelfRef.debug_stage1_o = vlSelfRef.simple_alu__DOT__stage1_result;
        vlSelfRef.simple_alu__DOT__debug_stage1_o = vlSelfRef.simple_alu__DOT__stage1_result;
        vlSelfRef.simple_alu__DOT__stage2_result = vlSelfRef.simple_alu__DOT__stage1_result;
        vlSelfRef.simple_alu__DOT__stage2_overflow 
            = vlSelfRef.simple_alu__DOT__stage1_overflow;
        vlSelfRef.simple_alu__DOT__shift_amount = 0U;
        vlSelfRef.simple_alu__DOT__rotate_amount = 0U;
        vlSelfRef.simple_alu__DOT__stage2_result = vlSelfRef.simple_alu__DOT__stage1_result;
    }
    vlSelfRef.simple_alu__DOT__debug_flags_o = vlSelfRef.debug_flags_o;
    vlSelfRef.debug_stage2_o = vlSelfRef.simple_alu__DOT__stage2_result;
    vlSelfRef.simple_alu__DOT__debug_stage2_o = vlSelfRef.simple_alu__DOT__stage2_result;
}

void Vtop___024root___eval_triggers__ico(Vtop___024root* vlSelf);

bool Vtop___024root___eval_phase__ico(Vtop___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtop___024root___eval_phase__ico\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Init
    CData/*0:0*/ __VicoExecute;
    // Body
    Vtop___024root___eval_triggers__ico(vlSelf);
    __VicoExecute = vlSelfRef.__VicoTriggered.any();
    if (__VicoExecute) {
        Vtop___024root___eval_ico(vlSelf);
    }
    return (__VicoExecute);
}

void Vtop___024root___eval_act(Vtop___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtop___024root___eval_act\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
}

void Vtop___024root___nba_sequent__TOP__0(Vtop___024root* vlSelf);

void Vtop___024root___eval_nba(Vtop___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtop___024root___eval_nba\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    if ((3ULL & vlSelfRef.__VnbaTriggered.word(0U))) {
        Vtop___024root___nba_sequent__TOP__0(vlSelf);
    }
}

VL_INLINE_OPT void Vtop___024root___nba_sequent__TOP__0(Vtop___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtop___024root___nba_sequent__TOP__0\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    if (vlSelfRef.rst_n) {
        vlSelfRef.simple_alu__DOT__pipeline_counter 
            = ((IData)(vlSelfRef.simple_alu__DOT__input_valid_reg)
                ? (((2U == (IData)(vlSelfRef.simple_alu__DOT__operation_reg)) 
                    | (3U == (IData)(vlSelfRef.simple_alu__DOT__operation_reg)))
                    ? (3U & ((IData)(1U) + (IData)(vlSelfRef.simple_alu__DOT__pipeline_counter)))
                    : 3U) : 0U);
        if (vlSelfRef.simple_alu__DOT__computation_valid) {
            vlSelfRef.simple_alu__DOT__final_overflow 
                = vlSelfRef.simple_alu__DOT__stage2_overflow;
            vlSelfRef.simple_alu__DOT__final_result 
                = vlSelfRef.simple_alu__DOT__stage2_result;
        }
        if (((IData)(vlSelfRef.valid_i) & (IData)(vlSelfRef.simple_alu__DOT__ready_o))) {
            vlSelfRef.simple_alu__DOT__operand_a_reg 
                = vlSelfRef.a_i;
            vlSelfRef.simple_alu__DOT__operand_b_reg 
                = vlSelfRef.b_i;
            vlSelfRef.simple_alu__DOT__input_valid_reg = 1U;
            vlSelfRef.simple_alu__DOT__operation_reg 
                = vlSelfRef.op_i;
        } else if (vlSelfRef.simple_alu__DOT__computation_valid) {
            vlSelfRef.simple_alu__DOT__input_valid_reg = 0U;
        }
    } else {
        vlSelfRef.simple_alu__DOT__pipeline_counter = 0U;
        vlSelfRef.simple_alu__DOT__final_overflow = 0U;
        vlSelfRef.simple_alu__DOT__final_result = 0U;
        vlSelfRef.simple_alu__DOT__operand_a_reg = 0U;
        vlSelfRef.simple_alu__DOT__operand_b_reg = 0U;
        vlSelfRef.simple_alu__DOT__input_valid_reg = 0U;
        vlSelfRef.simple_alu__DOT__operation_reg = 0xfU;
    }
    vlSelfRef.simple_alu__DOT__valid_o = ((IData)(vlSelfRef.rst_n) 
                                          && (IData)(vlSelfRef.simple_alu__DOT__computation_valid));
    vlSelfRef.valid_o = vlSelfRef.simple_alu__DOT__valid_o;
    vlSelfRef.overflow_o = vlSelfRef.simple_alu__DOT__final_overflow;
    vlSelfRef.simple_alu__DOT__overflow_o = vlSelfRef.simple_alu__DOT__final_overflow;
    vlSelfRef.result_o = vlSelfRef.simple_alu__DOT__final_result;
    vlSelfRef.simple_alu__DOT__result_o = vlSelfRef.simple_alu__DOT__final_result;
    vlSelfRef.simple_alu__DOT__zero_o = (0U == vlSelfRef.simple_alu__DOT__final_result);
    vlSelfRef.zero_o = vlSelfRef.simple_alu__DOT__zero_o;
    vlSelfRef.simple_alu__DOT__ready_o = (1U & (~ (IData)(vlSelfRef.simple_alu__DOT__input_valid_reg)));
    vlSelfRef.simple_alu__DOT__computation_valid = 
        ((3U == (IData)(vlSelfRef.simple_alu__DOT__pipeline_counter)) 
         | ((2U != (IData)(vlSelfRef.simple_alu__DOT__operation_reg)) 
            & ((3U != (IData)(vlSelfRef.simple_alu__DOT__operation_reg)) 
               & (IData)(vlSelfRef.simple_alu__DOT__input_valid_reg))));
    vlSelfRef.simple_alu__DOT__stage1_result = 0U;
    vlSelfRef.simple_alu__DOT__stage1_overflow = 0U;
    vlSelfRef.simple_alu__DOT__mul_result = 0ULL;
    vlSelfRef.ready_o = vlSelfRef.simple_alu__DOT__ready_o;
    vlSelfRef.debug_flags_o = ((((IData)(vlSelfRef.simple_alu__DOT__final_overflow) 
                                 << 3U) | ((IData)(vlSelfRef.simple_alu__DOT__zero_o) 
                                           << 2U)) 
                               | (((IData)(vlSelfRef.simple_alu__DOT__computation_valid) 
                                   << 1U) | (IData)(vlSelfRef.simple_alu__DOT__input_valid_reg)));
    if ((8U & (IData)(vlSelfRef.simple_alu__DOT__operation_reg))) {
        vlSelfRef.simple_alu__DOT__stage1_result = vlSelfRef.simple_alu__DOT__operand_a_reg;
        vlSelfRef.debug_stage1_o = vlSelfRef.simple_alu__DOT__stage1_result;
        vlSelfRef.simple_alu__DOT__debug_stage1_o = vlSelfRef.simple_alu__DOT__stage1_result;
        vlSelfRef.simple_alu__DOT__stage2_result = vlSelfRef.simple_alu__DOT__stage1_result;
        vlSelfRef.simple_alu__DOT__stage2_overflow 
            = vlSelfRef.simple_alu__DOT__stage1_overflow;
        vlSelfRef.simple_alu__DOT__shift_amount = 0U;
        vlSelfRef.simple_alu__DOT__rotate_amount = 0U;
        if ((4U & (IData)(vlSelfRef.simple_alu__DOT__operation_reg))) {
            vlSelfRef.simple_alu__DOT__stage2_result 
                = ((2U & (IData)(vlSelfRef.simple_alu__DOT__operation_reg))
                    ? ((1U & (IData)(vlSelfRef.simple_alu__DOT__operation_reg))
                        ? vlSelfRef.simple_alu__DOT__stage1_result
                        : ((vlSelfRef.simple_alu__DOT__operand_a_reg 
                            == vlSelfRef.simple_alu__DOT__operand_b_reg)
                            ? 0U : ((vlSelfRef.simple_alu__DOT__operand_a_reg 
                                     > vlSelfRef.simple_alu__DOT__operand_b_reg)
                                     ? 1U : 0xffffffffU)))
                    : ((1U & (IData)(vlSelfRef.simple_alu__DOT__operation_reg))
                        ? ((vlSelfRef.simple_alu__DOT__operand_a_reg 
                            < vlSelfRef.simple_alu__DOT__operand_b_reg)
                            ? vlSelfRef.simple_alu__DOT__operand_a_reg
                            : vlSelfRef.simple_alu__DOT__operand_b_reg)
                        : ((vlSelfRef.simple_alu__DOT__operand_a_reg 
                            > vlSelfRef.simple_alu__DOT__operand_b_reg)
                            ? vlSelfRef.simple_alu__DOT__operand_a_reg
                            : vlSelfRef.simple_alu__DOT__operand_b_reg)));
        } else if ((2U & (IData)(vlSelfRef.simple_alu__DOT__operation_reg))) {
            if ((1U & (IData)(vlSelfRef.simple_alu__DOT__operation_reg))) {
                vlSelfRef.simple_alu__DOT__rotate_amount 
                    = (0x1fU & vlSelfRef.simple_alu__DOT__operand_b_reg);
                vlSelfRef.simple_alu__DOT__stage2_result 
                    = (VL_SHIFTR_III(32,32,6, vlSelfRef.simple_alu__DOT__stage1_result, (IData)(vlSelfRef.simple_alu__DOT__rotate_amount)) 
                       | VL_SHIFTL_III(32,32,32, vlSelfRef.simple_alu__DOT__stage1_result, 
                                       ((IData)(0x20U) 
                                        - (IData)(vlSelfRef.simple_alu__DOT__rotate_amount))));
            } else {
                vlSelfRef.simple_alu__DOT__rotate_amount 
                    = (0x1fU & vlSelfRef.simple_alu__DOT__operand_b_reg);
                vlSelfRef.simple_alu__DOT__stage2_result 
                    = (VL_SHIFTL_III(32,32,6, vlSelfRef.simple_alu__DOT__stage1_result, (IData)(vlSelfRef.simple_alu__DOT__rotate_amount)) 
                       | VL_SHIFTR_III(32,32,32, vlSelfRef.simple_alu__DOT__stage1_result, 
                                       ((IData)(0x20U) 
                                        - (IData)(vlSelfRef.simple_alu__DOT__rotate_amount))));
            }
        } else if ((1U & (IData)(vlSelfRef.simple_alu__DOT__operation_reg))) {
            vlSelfRef.simple_alu__DOT__shift_amount 
                = (0x3fU & vlSelfRef.simple_alu__DOT__operand_b_reg);
            vlSelfRef.simple_alu__DOT__stage2_result 
                = ((0x20U > (IData)(vlSelfRef.simple_alu__DOT__shift_amount))
                    ? VL_SHIFTR_III(32,32,6, vlSelfRef.simple_alu__DOT__stage1_result, (IData)(vlSelfRef.simple_alu__DOT__shift_amount))
                    : 0U);
        } else {
            vlSelfRef.simple_alu__DOT__shift_amount 
                = (0x3fU & vlSelfRef.simple_alu__DOT__operand_b_reg);
            if ((0x20U > (IData)(vlSelfRef.simple_alu__DOT__shift_amount))) {
                vlSelfRef.simple_alu__DOT__stage2_result 
                    = VL_SHIFTL_III(32,32,6, vlSelfRef.simple_alu__DOT__stage1_result, (IData)(vlSelfRef.simple_alu__DOT__shift_amount));
                vlSelfRef.simple_alu__DOT__stage2_overflow 
                    = (0U != VL_SHIFTR_III(32,32,32, vlSelfRef.simple_alu__DOT__stage1_result, 
                                           ((IData)(0x20U) 
                                            - (IData)(vlSelfRef.simple_alu__DOT__shift_amount))));
            } else {
                vlSelfRef.simple_alu__DOT__stage2_result = 0U;
                vlSelfRef.simple_alu__DOT__stage2_overflow 
                    = (0U != vlSelfRef.simple_alu__DOT__stage1_result);
            }
        }
    } else {
        if ((4U & (IData)(vlSelfRef.simple_alu__DOT__operation_reg))) {
            vlSelfRef.simple_alu__DOT__stage1_result 
                = ((2U & (IData)(vlSelfRef.simple_alu__DOT__operation_reg))
                    ? ((1U & (IData)(vlSelfRef.simple_alu__DOT__operation_reg))
                        ? (~ vlSelfRef.simple_alu__DOT__operand_a_reg)
                        : (vlSelfRef.simple_alu__DOT__operand_a_reg 
                           ^ vlSelfRef.simple_alu__DOT__operand_b_reg))
                    : ((1U & (IData)(vlSelfRef.simple_alu__DOT__operation_reg))
                        ? (vlSelfRef.simple_alu__DOT__operand_a_reg 
                           | vlSelfRef.simple_alu__DOT__operand_b_reg)
                        : (vlSelfRef.simple_alu__DOT__operand_a_reg 
                           & vlSelfRef.simple_alu__DOT__operand_b_reg)));
        } else if ((2U & (IData)(vlSelfRef.simple_alu__DOT__operation_reg))) {
            if ((1U & (IData)(vlSelfRef.simple_alu__DOT__operation_reg))) {
                if ((0U != vlSelfRef.simple_alu__DOT__operand_b_reg)) {
                    vlSelfRef.simple_alu__DOT__stage1_result 
                        = VL_DIV_III(32, vlSelfRef.simple_alu__DOT__operand_a_reg, vlSelfRef.simple_alu__DOT__operand_b_reg);
                    vlSelfRef.simple_alu__DOT__stage1_overflow = 0U;
                } else {
                    vlSelfRef.simple_alu__DOT__stage1_result = 0xffffffffU;
                    vlSelfRef.simple_alu__DOT__stage1_overflow = 1U;
                }
            } else {
                vlSelfRef.simple_alu__DOT__mul_result 
                    = ((QData)((IData)(vlSelfRef.simple_alu__DOT__operand_a_reg)) 
                       * (QData)((IData)(vlSelfRef.simple_alu__DOT__operand_b_reg)));
                vlSelfRef.simple_alu__DOT__stage1_result 
                    = (IData)(vlSelfRef.simple_alu__DOT__mul_result);
                vlSelfRef.simple_alu__DOT__stage1_overflow 
                    = (0U != (IData)((vlSelfRef.simple_alu__DOT__mul_result 
                                      >> 0x20U)));
            }
        } else if ((1U & (IData)(vlSelfRef.simple_alu__DOT__operation_reg))) {
            vlSelfRef.simple_alu__DOT__stage1_overflow 
                = (1U & (IData)((1ULL & (((QData)((IData)(vlSelfRef.simple_alu__DOT__operand_a_reg)) 
                                          - (QData)((IData)(vlSelfRef.simple_alu__DOT__operand_b_reg))) 
                                         >> 0x20U))));
            vlSelfRef.simple_alu__DOT__stage1_result 
                = (vlSelfRef.simple_alu__DOT__operand_a_reg 
                   - vlSelfRef.simple_alu__DOT__operand_b_reg);
        } else {
            vlSelfRef.simple_alu__DOT__stage1_overflow 
                = (1U & (IData)((1ULL & (((QData)((IData)(vlSelfRef.simple_alu__DOT__operand_a_reg)) 
                                          + (QData)((IData)(vlSelfRef.simple_alu__DOT__operand_b_reg))) 
                                         >> 0x20U))));
            vlSelfRef.simple_alu__DOT__stage1_result 
                = (vlSelfRef.simple_alu__DOT__operand_a_reg 
                   + vlSelfRef.simple_alu__DOT__operand_b_reg);
        }
        vlSelfRef.debug_stage1_o = vlSelfRef.simple_alu__DOT__stage1_result;
        vlSelfRef.simple_alu__DOT__debug_stage1_o = vlSelfRef.simple_alu__DOT__stage1_result;
        vlSelfRef.simple_alu__DOT__stage2_result = vlSelfRef.simple_alu__DOT__stage1_result;
        vlSelfRef.simple_alu__DOT__stage2_overflow 
            = vlSelfRef.simple_alu__DOT__stage1_overflow;
        vlSelfRef.simple_alu__DOT__shift_amount = 0U;
        vlSelfRef.simple_alu__DOT__rotate_amount = 0U;
        vlSelfRef.simple_alu__DOT__stage2_result = vlSelfRef.simple_alu__DOT__stage1_result;
    }
    vlSelfRef.simple_alu__DOT__debug_flags_o = vlSelfRef.debug_flags_o;
    vlSelfRef.debug_stage2_o = vlSelfRef.simple_alu__DOT__stage2_result;
    vlSelfRef.simple_alu__DOT__debug_stage2_o = vlSelfRef.simple_alu__DOT__stage2_result;
}

void Vtop___024root___eval_triggers__act(Vtop___024root* vlSelf);

bool Vtop___024root___eval_phase__act(Vtop___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtop___024root___eval_phase__act\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Init
    VlTriggerVec<2> __VpreTriggered;
    CData/*0:0*/ __VactExecute;
    // Body
    Vtop___024root___eval_triggers__act(vlSelf);
    __VactExecute = vlSelfRef.__VactTriggered.any();
    if (__VactExecute) {
        __VpreTriggered.andNot(vlSelfRef.__VactTriggered, vlSelfRef.__VnbaTriggered);
        vlSelfRef.__VnbaTriggered.thisOr(vlSelfRef.__VactTriggered);
        Vtop___024root___eval_act(vlSelf);
    }
    return (__VactExecute);
}

bool Vtop___024root___eval_phase__nba(Vtop___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtop___024root___eval_phase__nba\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Init
    CData/*0:0*/ __VnbaExecute;
    // Body
    __VnbaExecute = vlSelfRef.__VnbaTriggered.any();
    if (__VnbaExecute) {
        Vtop___024root___eval_nba(vlSelf);
        vlSelfRef.__VnbaTriggered.clear();
    }
    return (__VnbaExecute);
}

#ifdef VL_DEBUG
VL_ATTR_COLD void Vtop___024root___dump_triggers__ico(Vtop___024root* vlSelf);
#endif  // VL_DEBUG
#ifdef VL_DEBUG
VL_ATTR_COLD void Vtop___024root___dump_triggers__nba(Vtop___024root* vlSelf);
#endif  // VL_DEBUG
#ifdef VL_DEBUG
VL_ATTR_COLD void Vtop___024root___dump_triggers__act(Vtop___024root* vlSelf);
#endif  // VL_DEBUG

void Vtop___024root___eval(Vtop___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtop___024root___eval\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Init
    IData/*31:0*/ __VicoIterCount;
    CData/*0:0*/ __VicoContinue;
    IData/*31:0*/ __VnbaIterCount;
    CData/*0:0*/ __VnbaContinue;
    // Body
    __VicoIterCount = 0U;
    vlSelfRef.__VicoFirstIteration = 1U;
    __VicoContinue = 1U;
    while (__VicoContinue) {
        if (VL_UNLIKELY(((0x64U < __VicoIterCount)))) {
#ifdef VL_DEBUG
            Vtop___024root___dump_triggers__ico(vlSelf);
#endif
            VL_FATAL_MT("/home/yanggl/code/BICSdifftest/examples/simple_alu/rtl/simple_alu.sv", 8, "", "Input combinational region did not converge.");
        }
        __VicoIterCount = ((IData)(1U) + __VicoIterCount);
        __VicoContinue = 0U;
        if (Vtop___024root___eval_phase__ico(vlSelf)) {
            __VicoContinue = 1U;
        }
        vlSelfRef.__VicoFirstIteration = 0U;
    }
    __VnbaIterCount = 0U;
    __VnbaContinue = 1U;
    while (__VnbaContinue) {
        if (VL_UNLIKELY(((0x64U < __VnbaIterCount)))) {
#ifdef VL_DEBUG
            Vtop___024root___dump_triggers__nba(vlSelf);
#endif
            VL_FATAL_MT("/home/yanggl/code/BICSdifftest/examples/simple_alu/rtl/simple_alu.sv", 8, "", "NBA region did not converge.");
        }
        __VnbaIterCount = ((IData)(1U) + __VnbaIterCount);
        __VnbaContinue = 0U;
        vlSelfRef.__VactIterCount = 0U;
        vlSelfRef.__VactContinue = 1U;
        while (vlSelfRef.__VactContinue) {
            if (VL_UNLIKELY(((0x64U < vlSelfRef.__VactIterCount)))) {
#ifdef VL_DEBUG
                Vtop___024root___dump_triggers__act(vlSelf);
#endif
                VL_FATAL_MT("/home/yanggl/code/BICSdifftest/examples/simple_alu/rtl/simple_alu.sv", 8, "", "Active region did not converge.");
            }
            vlSelfRef.__VactIterCount = ((IData)(1U) 
                                         + vlSelfRef.__VactIterCount);
            vlSelfRef.__VactContinue = 0U;
            if (Vtop___024root___eval_phase__act(vlSelf)) {
                vlSelfRef.__VactContinue = 1U;
            }
        }
        if (Vtop___024root___eval_phase__nba(vlSelf)) {
            __VnbaContinue = 1U;
        }
    }
}

#ifdef VL_DEBUG
void Vtop___024root___eval_debug_assertions(Vtop___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtop___024root___eval_debug_assertions\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    if (VL_UNLIKELY(((vlSelfRef.clk & 0xfeU)))) {
        Verilated::overWidthError("clk");}
    if (VL_UNLIKELY(((vlSelfRef.rst_n & 0xfeU)))) {
        Verilated::overWidthError("rst_n");}
    if (VL_UNLIKELY(((vlSelfRef.valid_i & 0xfeU)))) {
        Verilated::overWidthError("valid_i");}
    if (VL_UNLIKELY(((vlSelfRef.op_i & 0xf0U)))) {
        Verilated::overWidthError("op_i");}
}
#endif  // VL_DEBUG
