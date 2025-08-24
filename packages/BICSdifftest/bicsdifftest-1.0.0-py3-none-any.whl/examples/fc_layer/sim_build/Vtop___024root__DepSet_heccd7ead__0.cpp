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
    vlSelfRef.fc_layer__DOT__clk = vlSelfRef.clk;
    vlSelfRef.fc_layer__DOT__rst_n = vlSelfRef.rst_n;
    vlSelfRef.fc_layer__DOT__mode_i = vlSelfRef.mode_i;
    vlSelfRef.fc_layer__DOT__valid_i = vlSelfRef.valid_i;
    vlSelfRef.fc_layer__DOT__weight_addr_i = vlSelfRef.weight_addr_i;
    vlSelfRef.fc_layer__DOT__weight_data_i = vlSelfRef.weight_data_i;
    vlSelfRef.fc_layer__DOT__weight_we_i = vlSelfRef.weight_we_i;
    IData/*31:0*/ __Vilp1;
    __Vilp1 = 0U;
    while ((__Vilp1 <= 0x31U)) {
        vlSelfRef.fc_layer__DOT__input_data_i[__Vilp1] 
            = vlSelfRef.input_data_i[__Vilp1];
        __Vilp1 = ((IData)(1U) + __Vilp1);
    }
    vlSelfRef.fc_layer__DOT__bias_addr_i = vlSelfRef.bias_addr_i;
    vlSelfRef.fc_layer__DOT__bias_data_i = vlSelfRef.bias_data_i;
    vlSelfRef.fc_layer__DOT__bias_we_i = vlSelfRef.bias_we_i;
    vlSelfRef.output_data_o[0U] = vlSelfRef.fc_layer__DOT__output_reg[0U];
    vlSelfRef.output_data_o[1U] = vlSelfRef.fc_layer__DOT__output_reg[1U];
    vlSelfRef.output_data_o[2U] = vlSelfRef.fc_layer__DOT__output_reg[2U];
    vlSelfRef.output_data_o[3U] = vlSelfRef.fc_layer__DOT__output_reg[3U];
    vlSelfRef.output_data_o[4U] = vlSelfRef.fc_layer__DOT__output_reg[4U];
    vlSelfRef.fc_layer__DOT__output_data_o[0U] = vlSelfRef.fc_layer__DOT__output_reg[0U];
    vlSelfRef.fc_layer__DOT__output_data_o[1U] = vlSelfRef.fc_layer__DOT__output_reg[1U];
    vlSelfRef.fc_layer__DOT__output_data_o[2U] = vlSelfRef.fc_layer__DOT__output_reg[2U];
    vlSelfRef.fc_layer__DOT__output_data_o[3U] = vlSelfRef.fc_layer__DOT__output_reg[3U];
    vlSelfRef.fc_layer__DOT__output_data_o[4U] = vlSelfRef.fc_layer__DOT__output_reg[4U];
    vlSelfRef.valid_o = vlSelfRef.fc_layer__DOT__valid_o;
    vlSelfRef.fc_layer__DOT__input_counter_next = vlSelfRef.fc_layer__DOT__input_counter;
    vlSelfRef.fc_layer__DOT__output_counter_next = vlSelfRef.fc_layer__DOT__output_counter;
    vlSelfRef.debug_accumulator_o = (0xffffU & (IData)(vlSelfRef.fc_layer__DOT__accumulator));
    vlSelfRef.fc_layer__DOT__next_state = vlSelfRef.fc_layer__DOT__current_state;
    vlSelfRef.debug_state_o = (((IData)(vlSelfRef.fc_layer__DOT__current_state) 
                                << 1U) | (IData)(vlSelfRef.mode_i));
    vlSelfRef.fc_layer__DOT__ready_o = ((0U == (IData)(vlSelfRef.fc_layer__DOT__current_state)) 
                                        | ((~ (IData)(vlSelfRef.mode_i)) 
                                           & ((1U == (IData)(vlSelfRef.fc_layer__DOT__current_state)) 
                                              | (2U 
                                                 == (IData)(vlSelfRef.fc_layer__DOT__current_state)))));
    vlSelfRef.debug_addr_counter_o = ((0x3f8U & ((IData)(vlSelfRef.fc_layer__DOT__input_counter) 
                                                 << 3U)) 
                                      | (7U & (IData)(vlSelfRef.fc_layer__DOT__output_counter)));
    vlSelfRef.fc_layer__DOT__output_reg_next[0U] = 
        vlSelfRef.fc_layer__DOT__output_reg[0U];
    vlSelfRef.fc_layer__DOT__output_reg_next[1U] = 
        vlSelfRef.fc_layer__DOT__output_reg[1U];
    vlSelfRef.fc_layer__DOT__output_reg_next[2U] = 
        vlSelfRef.fc_layer__DOT__output_reg[2U];
    vlSelfRef.fc_layer__DOT__output_reg_next[3U] = 
        vlSelfRef.fc_layer__DOT__output_reg[3U];
    vlSelfRef.fc_layer__DOT__output_reg_next[4U] = 
        vlSelfRef.fc_layer__DOT__output_reg[4U];
    vlSelfRef.fc_layer__DOT__final_result = 0U;
    vlSelfRef.fc_layer__DOT__overflow_flag = 0U;
    vlSelfRef.fc_layer__DOT__underflow_flag = 0U;
    vlSelfRef.fc_layer__DOT__computation_done = 0U;
    vlSelfRef.fc_layer__DOT__accumulator_next = vlSelfRef.fc_layer__DOT__accumulator;
    vlSelfRef.fc_layer__DOT__mult_result_full = 0U;
    vlSelfRef.fc_layer__DOT__mult_result = 0U;
    if ((4U & (IData)(vlSelfRef.fc_layer__DOT__current_state))) {
        if ((1U & (~ ((IData)(vlSelfRef.fc_layer__DOT__current_state) 
                      >> 1U)))) {
            if ((1U & (~ (IData)(vlSelfRef.fc_layer__DOT__current_state)))) {
                if ((0x63U != (IData)(vlSelfRef.fc_layer__DOT__input_counter))) {
                    vlSelfRef.fc_layer__DOT__input_counter_next 
                        = (0x3ffU & ((IData)(1U) + (IData)(vlSelfRef.fc_layer__DOT__input_counter)));
                }
                vlSelfRef.fc_layer__DOT__mult_result_full 
                    = VL_MULS_III(32, VL_EXTENDS_II(32,16, 
                                                    ((0x63fU 
                                                      >= 
                                                      (0x7ffU 
                                                       & VL_SHIFTL_III(11,32,32, (IData)(vlSelfRef.fc_layer__DOT__input_counter), 4U)))
                                                      ? 
                                                     (0xffffU 
                                                      & (((0U 
                                                           == 
                                                           (0x1fU 
                                                            & VL_SHIFTL_III(11,32,32, (IData)(vlSelfRef.fc_layer__DOT__input_counter), 4U)))
                                                           ? 0U
                                                           : 
                                                          (vlSelfRef.fc_layer__DOT__input_reg[
                                                           (((IData)(0xfU) 
                                                             + 
                                                             (0x7ffU 
                                                              & VL_SHIFTL_III(11,32,32, (IData)(vlSelfRef.fc_layer__DOT__input_counter), 4U))) 
                                                            >> 5U)] 
                                                           << 
                                                           ((IData)(0x20U) 
                                                            - 
                                                            (0x1fU 
                                                             & VL_SHIFTL_III(11,32,32, (IData)(vlSelfRef.fc_layer__DOT__input_counter), 4U))))) 
                                                         | (vlSelfRef.fc_layer__DOT__input_reg[
                                                            (0x3fU 
                                                             & (VL_SHIFTL_III(11,32,32, (IData)(vlSelfRef.fc_layer__DOT__input_counter), 4U) 
                                                                >> 5U))] 
                                                            >> 
                                                            (0x1fU 
                                                             & VL_SHIFTL_III(11,32,32, (IData)(vlSelfRef.fc_layer__DOT__input_counter), 4U)))))
                                                      : 0U)), 
                                  VL_EXTENDS_II(32,16, 
                                                ((0x3e7fU 
                                                  >= 
                                                  (0x3fffU 
                                                   & (((IData)(0xa0U) 
                                                       * (IData)(vlSelfRef.fc_layer__DOT__input_counter)) 
                                                      + 
                                                      (0xffU 
                                                       & VL_SHIFTL_III(8,32,32, (IData)(vlSelfRef.fc_layer__DOT__output_counter), 4U)))))
                                                  ? 
                                                 (0xffffU 
                                                  & (((0U 
                                                       == 
                                                       (0x1fU 
                                                        & (((IData)(0xa0U) 
                                                            * (IData)(vlSelfRef.fc_layer__DOT__input_counter)) 
                                                           + 
                                                           (0xffU 
                                                            & VL_SHIFTL_III(8,32,32, (IData)(vlSelfRef.fc_layer__DOT__output_counter), 4U)))))
                                                       ? 0U
                                                       : 
                                                      (vlSelfRef.fc_layer__DOT__weight_memory[
                                                       (((IData)(0xfU) 
                                                         + 
                                                         (0x3fffU 
                                                          & (((IData)(0xa0U) 
                                                              * (IData)(vlSelfRef.fc_layer__DOT__input_counter)) 
                                                             + 
                                                             (0xffU 
                                                              & VL_SHIFTL_III(8,32,32, (IData)(vlSelfRef.fc_layer__DOT__output_counter), 4U))))) 
                                                        >> 5U)] 
                                                       << 
                                                       ((IData)(0x20U) 
                                                        - 
                                                        (0x1fU 
                                                         & (((IData)(0xa0U) 
                                                             * (IData)(vlSelfRef.fc_layer__DOT__input_counter)) 
                                                            + 
                                                            (0xffU 
                                                             & VL_SHIFTL_III(8,32,32, (IData)(vlSelfRef.fc_layer__DOT__output_counter), 4U))))))) 
                                                     | (vlSelfRef.fc_layer__DOT__weight_memory[
                                                        (0x1ffU 
                                                         & ((((IData)(0xa0U) 
                                                              * (IData)(vlSelfRef.fc_layer__DOT__input_counter)) 
                                                             + 
                                                             (0xffU 
                                                              & VL_SHIFTL_III(8,32,32, (IData)(vlSelfRef.fc_layer__DOT__output_counter), 4U))) 
                                                            >> 5U))] 
                                                        >> 
                                                        (0x1fU 
                                                         & (((IData)(0xa0U) 
                                                             * (IData)(vlSelfRef.fc_layer__DOT__input_counter)) 
                                                            + 
                                                            (0xffU 
                                                             & VL_SHIFTL_III(8,32,32, (IData)(vlSelfRef.fc_layer__DOT__output_counter), 4U)))))))
                                                  : 0U)));
                vlSelfRef.fc_layer__DOT__mult_result 
                    = (0xffffU & (vlSelfRef.fc_layer__DOT__mult_result_full 
                                  >> 8U));
                vlSelfRef.fc_layer__DOT__accumulator_next 
                    = (0x3ffffffffffULL & (vlSelfRef.fc_layer__DOT__accumulator 
                                           + (((QData)((IData)(
                                                               (0x3ffffffU 
                                                                & (- (IData)(
                                                                             (1U 
                                                                              & ((IData)(vlSelfRef.fc_layer__DOT__mult_result) 
                                                                                >> 0xfU))))))) 
                                               << 0x10U) 
                                              | (QData)((IData)(vlSelfRef.fc_layer__DOT__mult_result)))));
            }
            if ((1U & (IData)(vlSelfRef.fc_layer__DOT__current_state))) {
                if ((9U == (IData)(vlSelfRef.fc_layer__DOT__output_counter))) {
                    vlSelfRef.fc_layer__DOT__output_counter_next = 0U;
                    vlSelfRef.fc_layer__DOT__computation_done = 1U;
                } else {
                    vlSelfRef.fc_layer__DOT__output_counter_next 
                        = (0x3ffU & ((IData)(1U) + (IData)(vlSelfRef.fc_layer__DOT__output_counter)));
                }
                vlSelfRef.fc_layer__DOT__final_result 
                    = (0xffffU & (IData)(vlSelfRef.fc_layer__DOT__accumulator));
                vlSelfRef.fc_layer__DOT____Vlvbound_hc325c5e8__0 
                    = vlSelfRef.fc_layer__DOT__final_result;
                if ((0x9fU >= (0xffU & VL_SHIFTL_III(8,32,32, (IData)(vlSelfRef.fc_layer__DOT__output_counter), 4U)))) {
                    VL_ASSIGNSEL_WI(160,16,(0xffU & 
                                            VL_SHIFTL_III(8,32,32, (IData)(vlSelfRef.fc_layer__DOT__output_counter), 4U)), vlSelfRef.fc_layer__DOT__output_reg_next, vlSelfRef.fc_layer__DOT____Vlvbound_hc325c5e8__0);
                }
                vlSelfRef.fc_layer__DOT__overflow_flag = 0U;
                vlSelfRef.fc_layer__DOT__underflow_flag = 0U;
            }
        }
        if ((2U & (IData)(vlSelfRef.fc_layer__DOT__current_state))) {
            vlSelfRef.fc_layer__DOT__next_state = 0U;
        } else if ((1U & (IData)(vlSelfRef.fc_layer__DOT__current_state))) {
            vlSelfRef.fc_layer__DOT__next_state = (
                                                   (9U 
                                                    == (IData)(vlSelfRef.fc_layer__DOT__output_counter))
                                                    ? 0U
                                                    : 3U);
        } else if ((0x63U == (IData)(vlSelfRef.fc_layer__DOT__input_counter))) {
            vlSelfRef.fc_layer__DOT__next_state = 5U;
        }
    } else if ((2U & (IData)(vlSelfRef.fc_layer__DOT__current_state))) {
        if ((1U & (IData)(vlSelfRef.fc_layer__DOT__current_state))) {
            vlSelfRef.fc_layer__DOT__input_counter_next = 0U;
            vlSelfRef.fc_layer__DOT__next_state = 4U;
            vlSelfRef.fc_layer__DOT__accumulator_next 
                = (((QData)((IData)((0x3ffffffU & (- (IData)(
                                                             ((0x9fU 
                                                               >= 
                                                               (0xffU 
                                                                & ((IData)(0xfU) 
                                                                   + 
                                                                   VL_SHIFTL_III(8,32,32, (IData)(vlSelfRef.fc_layer__DOT__output_counter), 4U)))) 
                                                              && (1U 
                                                                  & (vlSelfRef.fc_layer__DOT__bias_memory[
                                                                     (7U 
                                                                      & (((IData)(0xfU) 
                                                                          + 
                                                                          VL_SHIFTL_III(8,32,32, (IData)(vlSelfRef.fc_layer__DOT__output_counter), 4U)) 
                                                                         >> 5U))] 
                                                                     >> 
                                                                     (0x1fU 
                                                                      & ((IData)(0xfU) 
                                                                         + 
                                                                         VL_SHIFTL_III(8,32,32, (IData)(vlSelfRef.fc_layer__DOT__output_counter), 4U))))))))))) 
                    << 0x10U) | (QData)((IData)(((0x9fU 
                                                  >= 
                                                  (0xffU 
                                                   & VL_SHIFTL_III(8,32,32, (IData)(vlSelfRef.fc_layer__DOT__output_counter), 4U)))
                                                  ? 
                                                 (0xffffU 
                                                  & (((0U 
                                                       == 
                                                       (0x1fU 
                                                        & VL_SHIFTL_III(8,32,32, (IData)(vlSelfRef.fc_layer__DOT__output_counter), 4U)))
                                                       ? 0U
                                                       : 
                                                      (vlSelfRef.fc_layer__DOT__bias_memory[
                                                       (((IData)(0xfU) 
                                                         + 
                                                         (0xffU 
                                                          & VL_SHIFTL_III(8,32,32, (IData)(vlSelfRef.fc_layer__DOT__output_counter), 4U))) 
                                                        >> 5U)] 
                                                       << 
                                                       ((IData)(0x20U) 
                                                        - 
                                                        (0x1fU 
                                                         & VL_SHIFTL_III(8,32,32, (IData)(vlSelfRef.fc_layer__DOT__output_counter), 4U))))) 
                                                     | (vlSelfRef.fc_layer__DOT__bias_memory[
                                                        (7U 
                                                         & (VL_SHIFTL_III(8,32,32, (IData)(vlSelfRef.fc_layer__DOT__output_counter), 4U) 
                                                            >> 5U))] 
                                                        >> 
                                                        (0x1fU 
                                                         & VL_SHIFTL_III(8,32,32, (IData)(vlSelfRef.fc_layer__DOT__output_counter), 4U)))))
                                                  : 0U))));
        } else if (vlSelfRef.mode_i) {
            vlSelfRef.fc_layer__DOT__input_counter_next = 0U;
            vlSelfRef.fc_layer__DOT__next_state = 3U;
            vlSelfRef.fc_layer__DOT__accumulator_next = 0ULL;
        }
        if ((1U & (~ (IData)(vlSelfRef.fc_layer__DOT__current_state)))) {
            if (vlSelfRef.mode_i) {
                vlSelfRef.fc_layer__DOT__output_counter_next = 0U;
            }
        }
    } else if ((1U & (IData)(vlSelfRef.fc_layer__DOT__current_state))) {
        if (vlSelfRef.mode_i) {
            vlSelfRef.fc_layer__DOT__input_counter_next = 0U;
            vlSelfRef.fc_layer__DOT__output_counter_next = 0U;
            vlSelfRef.fc_layer__DOT__next_state = 3U;
            vlSelfRef.fc_layer__DOT__accumulator_next = 0ULL;
        }
    } else if (vlSelfRef.valid_i) {
        if (vlSelfRef.mode_i) {
            vlSelfRef.fc_layer__DOT__input_counter_next = 0U;
            vlSelfRef.fc_layer__DOT__output_counter_next = 0U;
            vlSelfRef.fc_layer__DOT__next_state = 3U;
            vlSelfRef.fc_layer__DOT__accumulator_next = 0ULL;
        } else {
            vlSelfRef.fc_layer__DOT__next_state = 1U;
        }
    }
    vlSelfRef.fc_layer__DOT__debug_accumulator_o = vlSelfRef.debug_accumulator_o;
    vlSelfRef.fc_layer__DOT__debug_state_o = vlSelfRef.debug_state_o;
    vlSelfRef.ready_o = vlSelfRef.fc_layer__DOT__ready_o;
    vlSelfRef.fc_layer__DOT__debug_addr_counter_o = vlSelfRef.debug_addr_counter_o;
    vlSelfRef.debug_flags_o = ((((IData)(vlSelfRef.fc_layer__DOT__computation_done) 
                                 << 3U) | ((IData)(vlSelfRef.fc_layer__DOT__overflow_flag) 
                                           << 2U)) 
                               | (((IData)(vlSelfRef.fc_layer__DOT__underflow_flag) 
                                   << 1U) | (IData)(vlSelfRef.fc_layer__DOT__valid_o)));
    vlSelfRef.fc_layer__DOT__debug_flags_o = vlSelfRef.debug_flags_o;
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

extern const VlWide<50>/*1599:0*/ Vtop__ConstPool__CONST_ha4affa7d_0;

VL_INLINE_OPT void Vtop___024root___nba_sequent__TOP__0(Vtop___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtop___024root___nba_sequent__TOP__0\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    if ((1U & (~ (IData)(vlSelfRef.rst_n)))) {
        vlSelfRef.fc_layer__DOT__unnamedblk3__DOT__j = 1U;
        vlSelfRef.fc_layer__DOT__unnamedblk3__DOT__j = 2U;
        vlSelfRef.fc_layer__DOT__unnamedblk3__DOT__j = 3U;
        vlSelfRef.fc_layer__DOT__unnamedblk3__DOT__j = 4U;
        vlSelfRef.fc_layer__DOT__unnamedblk3__DOT__j = 5U;
        vlSelfRef.fc_layer__DOT__unnamedblk3__DOT__j = 6U;
        vlSelfRef.fc_layer__DOT__unnamedblk3__DOT__j = 7U;
        vlSelfRef.fc_layer__DOT__unnamedblk3__DOT__j = 8U;
        vlSelfRef.fc_layer__DOT__unnamedblk3__DOT__j = 9U;
        vlSelfRef.fc_layer__DOT__unnamedblk3__DOT__j = 0xaU;
    }
    vlSelfRef.fc_layer__DOT__valid_o = ((IData)(vlSelfRef.rst_n) 
                                        && (IData)(vlSelfRef.fc_layer__DOT__computation_done));
    if (vlSelfRef.rst_n) {
        if (((IData)(vlSelfRef.bias_we_i) & (~ (IData)(vlSelfRef.mode_i)))) {
            if ((0xaU > (IData)(vlSelfRef.bias_addr_i))) {
                vlSelfRef.fc_layer__DOT____Vlvbound_h92854779__0 
                    = vlSelfRef.bias_data_i;
                if ((0x9fU >= (0xffU & VL_SHIFTL_III(8,32,32, (IData)(vlSelfRef.bias_addr_i), 4U)))) {
                    VL_ASSIGNSEL_WI(160,16,(0xffU & 
                                            VL_SHIFTL_III(8,32,32, (IData)(vlSelfRef.bias_addr_i), 4U)), vlSelfRef.fc_layer__DOT__bias_memory, vlSelfRef.fc_layer__DOT____Vlvbound_h92854779__0);
                }
            }
        }
        if ((((IData)(vlSelfRef.valid_i) & (IData)(vlSelfRef.fc_layer__DOT__ready_o)) 
             & (IData)(vlSelfRef.mode_i))) {
            IData/*31:0*/ __Vilp1;
            __Vilp1 = 0U;
            while ((__Vilp1 <= 0x31U)) {
                vlSelfRef.fc_layer__DOT__input_reg[__Vilp1] 
                    = vlSelfRef.input_data_i[__Vilp1];
                __Vilp1 = ((IData)(1U) + __Vilp1);
            }
        }
        if (vlSelfRef.fc_layer__DOT__computation_done) {
            vlSelfRef.fc_layer__DOT__output_reg[0U] 
                = vlSelfRef.fc_layer__DOT__output_reg_next[0U];
            vlSelfRef.fc_layer__DOT__output_reg[1U] 
                = vlSelfRef.fc_layer__DOT__output_reg_next[1U];
            vlSelfRef.fc_layer__DOT__output_reg[2U] 
                = vlSelfRef.fc_layer__DOT__output_reg_next[2U];
            vlSelfRef.fc_layer__DOT__output_reg[3U] 
                = vlSelfRef.fc_layer__DOT__output_reg_next[3U];
            vlSelfRef.fc_layer__DOT__output_reg[4U] 
                = vlSelfRef.fc_layer__DOT__output_reg_next[4U];
        }
        if (((IData)(vlSelfRef.weight_we_i) & (~ (IData)(vlSelfRef.mode_i)))) {
            vlSelfRef.fc_layer__DOT__unnamedblk4__DOT__input_idx 
                = (0x7fU & ((IData)(vlSelfRef.weight_addr_i) 
                            >> 3U));
            vlSelfRef.fc_layer__DOT__unnamedblk4__DOT__output_idx 
                = (7U & (IData)(vlSelfRef.weight_addr_i));
            if (((0x64U > (IData)(vlSelfRef.fc_layer__DOT__unnamedblk4__DOT__input_idx)) 
                 & (0xaU > (IData)(vlSelfRef.fc_layer__DOT__unnamedblk4__DOT__output_idx)))) {
                vlSelfRef.fc_layer__DOT____Vlvbound_h8449f1d8__0 
                    = vlSelfRef.weight_data_i;
                if ((0x3e7fU >= (0x3fffU & (((IData)(0xa0U) 
                                             * (IData)(vlSelfRef.fc_layer__DOT__unnamedblk4__DOT__input_idx)) 
                                            + (0xffU 
                                               & VL_SHIFTL_III(8,32,32, (IData)(vlSelfRef.fc_layer__DOT__unnamedblk4__DOT__output_idx), 4U)))))) {
                    VL_ASSIGNSEL_WI(16000,16,(0x3fffU 
                                              & (((IData)(0xa0U) 
                                                  * (IData)(vlSelfRef.fc_layer__DOT__unnamedblk4__DOT__input_idx)) 
                                                 + 
                                                 (0xffU 
                                                  & VL_SHIFTL_III(8,32,32, (IData)(vlSelfRef.fc_layer__DOT__unnamedblk4__DOT__output_idx), 4U)))), vlSelfRef.fc_layer__DOT__weight_memory, vlSelfRef.fc_layer__DOT____Vlvbound_h8449f1d8__0);
                }
            }
        }
        vlSelfRef.fc_layer__DOT__input_counter = vlSelfRef.fc_layer__DOT__input_counter_next;
        vlSelfRef.fc_layer__DOT__accumulator = vlSelfRef.fc_layer__DOT__accumulator_next;
        vlSelfRef.fc_layer__DOT__output_counter = vlSelfRef.fc_layer__DOT__output_counter_next;
        vlSelfRef.fc_layer__DOT__current_state = vlSelfRef.fc_layer__DOT__next_state;
    } else {
        vlSelfRef.fc_layer__DOT__bias_memory[0U] = 0U;
        vlSelfRef.fc_layer__DOT__bias_memory[1U] = 0U;
        vlSelfRef.fc_layer__DOT__bias_memory[2U] = 0U;
        vlSelfRef.fc_layer__DOT__bias_memory[3U] = 0U;
        vlSelfRef.fc_layer__DOT__bias_memory[4U] = 0U;
        IData/*31:0*/ __Vilp2;
        __Vilp2 = 0U;
        while ((__Vilp2 <= 0x31U)) {
            vlSelfRef.fc_layer__DOT__input_reg[__Vilp2] 
                = Vtop__ConstPool__CONST_ha4affa7d_0[__Vilp2];
            __Vilp2 = ((IData)(1U) + __Vilp2);
        }
        vlSelfRef.fc_layer__DOT__output_reg[0U] = 0U;
        vlSelfRef.fc_layer__DOT__output_reg[1U] = 0U;
        vlSelfRef.fc_layer__DOT__output_reg[2U] = 0U;
        vlSelfRef.fc_layer__DOT__output_reg[3U] = 0U;
        vlSelfRef.fc_layer__DOT__output_reg[4U] = 0U;
        vlSelfRef.fc_layer__DOT__unnamedblk1__DOT__i = 0U;
        while (VL_GTS_III(32, 0x64U, vlSelfRef.fc_layer__DOT__unnamedblk1__DOT__i)) {
            vlSelfRef.fc_layer__DOT____Vlvbound_hc62066ac__0 = 0U;
            if (VL_LIKELY(((0x3e7fU >= (0x3fffU & ((IData)(0xa0U) 
                                                   * vlSelfRef.fc_layer__DOT__unnamedblk1__DOT__i)))))) {
                VL_ASSIGNSEL_WI(16000,16,(0x3fffU & 
                                          ((IData)(0xa0U) 
                                           * vlSelfRef.fc_layer__DOT__unnamedblk1__DOT__i)), vlSelfRef.fc_layer__DOT__weight_memory, vlSelfRef.fc_layer__DOT____Vlvbound_hc62066ac__0);
            }
            vlSelfRef.fc_layer__DOT__unnamedblk1__DOT__unnamedblk2__DOT__j = 1U;
            vlSelfRef.fc_layer__DOT____Vlvbound_hc62066ac__0 = 0U;
            if (VL_LIKELY(((0x3e7fU >= (0x3fffU & ((IData)(0x10U) 
                                                   + 
                                                   ((IData)(0xa0U) 
                                                    * vlSelfRef.fc_layer__DOT__unnamedblk1__DOT__i))))))) {
                VL_ASSIGNSEL_WI(16000,16,(0x3fffU & 
                                          ((IData)(0x10U) 
                                           + ((IData)(0xa0U) 
                                              * vlSelfRef.fc_layer__DOT__unnamedblk1__DOT__i))), vlSelfRef.fc_layer__DOT__weight_memory, vlSelfRef.fc_layer__DOT____Vlvbound_hc62066ac__0);
            }
            vlSelfRef.fc_layer__DOT__unnamedblk1__DOT__unnamedblk2__DOT__j = 2U;
            vlSelfRef.fc_layer__DOT____Vlvbound_hc62066ac__0 = 0U;
            if (VL_LIKELY(((0x3e7fU >= (0x3fffU & ((IData)(0x20U) 
                                                   + 
                                                   ((IData)(0xa0U) 
                                                    * vlSelfRef.fc_layer__DOT__unnamedblk1__DOT__i))))))) {
                VL_ASSIGNSEL_WI(16000,16,(0x3fffU & 
                                          ((IData)(0x20U) 
                                           + ((IData)(0xa0U) 
                                              * vlSelfRef.fc_layer__DOT__unnamedblk1__DOT__i))), vlSelfRef.fc_layer__DOT__weight_memory, vlSelfRef.fc_layer__DOT____Vlvbound_hc62066ac__0);
            }
            vlSelfRef.fc_layer__DOT__unnamedblk1__DOT__unnamedblk2__DOT__j = 3U;
            vlSelfRef.fc_layer__DOT____Vlvbound_hc62066ac__0 = 0U;
            if (VL_LIKELY(((0x3e7fU >= (0x3fffU & ((IData)(0x30U) 
                                                   + 
                                                   ((IData)(0xa0U) 
                                                    * vlSelfRef.fc_layer__DOT__unnamedblk1__DOT__i))))))) {
                VL_ASSIGNSEL_WI(16000,16,(0x3fffU & 
                                          ((IData)(0x30U) 
                                           + ((IData)(0xa0U) 
                                              * vlSelfRef.fc_layer__DOT__unnamedblk1__DOT__i))), vlSelfRef.fc_layer__DOT__weight_memory, vlSelfRef.fc_layer__DOT____Vlvbound_hc62066ac__0);
            }
            vlSelfRef.fc_layer__DOT__unnamedblk1__DOT__unnamedblk2__DOT__j = 4U;
            vlSelfRef.fc_layer__DOT____Vlvbound_hc62066ac__0 = 0U;
            if (VL_LIKELY(((0x3e7fU >= (0x3fffU & ((IData)(0x40U) 
                                                   + 
                                                   ((IData)(0xa0U) 
                                                    * vlSelfRef.fc_layer__DOT__unnamedblk1__DOT__i))))))) {
                VL_ASSIGNSEL_WI(16000,16,(0x3fffU & 
                                          ((IData)(0x40U) 
                                           + ((IData)(0xa0U) 
                                              * vlSelfRef.fc_layer__DOT__unnamedblk1__DOT__i))), vlSelfRef.fc_layer__DOT__weight_memory, vlSelfRef.fc_layer__DOT____Vlvbound_hc62066ac__0);
            }
            vlSelfRef.fc_layer__DOT__unnamedblk1__DOT__unnamedblk2__DOT__j = 5U;
            vlSelfRef.fc_layer__DOT____Vlvbound_hc62066ac__0 = 0U;
            if (VL_LIKELY(((0x3e7fU >= (0x3fffU & ((IData)(0x50U) 
                                                   + 
                                                   ((IData)(0xa0U) 
                                                    * vlSelfRef.fc_layer__DOT__unnamedblk1__DOT__i))))))) {
                VL_ASSIGNSEL_WI(16000,16,(0x3fffU & 
                                          ((IData)(0x50U) 
                                           + ((IData)(0xa0U) 
                                              * vlSelfRef.fc_layer__DOT__unnamedblk1__DOT__i))), vlSelfRef.fc_layer__DOT__weight_memory, vlSelfRef.fc_layer__DOT____Vlvbound_hc62066ac__0);
            }
            vlSelfRef.fc_layer__DOT__unnamedblk1__DOT__unnamedblk2__DOT__j = 6U;
            vlSelfRef.fc_layer__DOT____Vlvbound_hc62066ac__0 = 0U;
            if (VL_LIKELY(((0x3e7fU >= (0x3fffU & ((IData)(0x60U) 
                                                   + 
                                                   ((IData)(0xa0U) 
                                                    * vlSelfRef.fc_layer__DOT__unnamedblk1__DOT__i))))))) {
                VL_ASSIGNSEL_WI(16000,16,(0x3fffU & 
                                          ((IData)(0x60U) 
                                           + ((IData)(0xa0U) 
                                              * vlSelfRef.fc_layer__DOT__unnamedblk1__DOT__i))), vlSelfRef.fc_layer__DOT__weight_memory, vlSelfRef.fc_layer__DOT____Vlvbound_hc62066ac__0);
            }
            vlSelfRef.fc_layer__DOT__unnamedblk1__DOT__unnamedblk2__DOT__j = 7U;
            vlSelfRef.fc_layer__DOT____Vlvbound_hc62066ac__0 = 0U;
            if (VL_LIKELY(((0x3e7fU >= (0x3fffU & ((IData)(0x70U) 
                                                   + 
                                                   ((IData)(0xa0U) 
                                                    * vlSelfRef.fc_layer__DOT__unnamedblk1__DOT__i))))))) {
                VL_ASSIGNSEL_WI(16000,16,(0x3fffU & 
                                          ((IData)(0x70U) 
                                           + ((IData)(0xa0U) 
                                              * vlSelfRef.fc_layer__DOT__unnamedblk1__DOT__i))), vlSelfRef.fc_layer__DOT__weight_memory, vlSelfRef.fc_layer__DOT____Vlvbound_hc62066ac__0);
            }
            vlSelfRef.fc_layer__DOT__unnamedblk1__DOT__unnamedblk2__DOT__j = 8U;
            vlSelfRef.fc_layer__DOT____Vlvbound_hc62066ac__0 = 0U;
            if (VL_LIKELY(((0x3e7fU >= (0x3fffU & ((IData)(0x80U) 
                                                   + 
                                                   ((IData)(0xa0U) 
                                                    * vlSelfRef.fc_layer__DOT__unnamedblk1__DOT__i))))))) {
                VL_ASSIGNSEL_WI(16000,16,(0x3fffU & 
                                          ((IData)(0x80U) 
                                           + ((IData)(0xa0U) 
                                              * vlSelfRef.fc_layer__DOT__unnamedblk1__DOT__i))), vlSelfRef.fc_layer__DOT__weight_memory, vlSelfRef.fc_layer__DOT____Vlvbound_hc62066ac__0);
            }
            vlSelfRef.fc_layer__DOT__unnamedblk1__DOT__unnamedblk2__DOT__j = 9U;
            vlSelfRef.fc_layer__DOT____Vlvbound_hc62066ac__0 = 0U;
            if (VL_LIKELY(((0x3e7fU >= (0x3fffU & ((IData)(0x90U) 
                                                   + 
                                                   ((IData)(0xa0U) 
                                                    * vlSelfRef.fc_layer__DOT__unnamedblk1__DOT__i))))))) {
                VL_ASSIGNSEL_WI(16000,16,(0x3fffU & 
                                          ((IData)(0x90U) 
                                           + ((IData)(0xa0U) 
                                              * vlSelfRef.fc_layer__DOT__unnamedblk1__DOT__i))), vlSelfRef.fc_layer__DOT__weight_memory, vlSelfRef.fc_layer__DOT____Vlvbound_hc62066ac__0);
            }
            vlSelfRef.fc_layer__DOT__unnamedblk1__DOT__unnamedblk2__DOT__j = 0xaU;
            vlSelfRef.fc_layer__DOT__unnamedblk1__DOT__i 
                = ((IData)(1U) + vlSelfRef.fc_layer__DOT__unnamedblk1__DOT__i);
        }
        vlSelfRef.fc_layer__DOT__input_counter = 0U;
        vlSelfRef.fc_layer__DOT__accumulator = 0ULL;
        vlSelfRef.fc_layer__DOT__output_counter = 0U;
        vlSelfRef.fc_layer__DOT__current_state = 0U;
    }
    vlSelfRef.valid_o = vlSelfRef.fc_layer__DOT__valid_o;
    vlSelfRef.output_data_o[0U] = vlSelfRef.fc_layer__DOT__output_reg[0U];
    vlSelfRef.output_data_o[1U] = vlSelfRef.fc_layer__DOT__output_reg[1U];
    vlSelfRef.output_data_o[2U] = vlSelfRef.fc_layer__DOT__output_reg[2U];
    vlSelfRef.output_data_o[3U] = vlSelfRef.fc_layer__DOT__output_reg[3U];
    vlSelfRef.output_data_o[4U] = vlSelfRef.fc_layer__DOT__output_reg[4U];
    vlSelfRef.fc_layer__DOT__output_data_o[0U] = vlSelfRef.fc_layer__DOT__output_reg[0U];
    vlSelfRef.fc_layer__DOT__output_data_o[1U] = vlSelfRef.fc_layer__DOT__output_reg[1U];
    vlSelfRef.fc_layer__DOT__output_data_o[2U] = vlSelfRef.fc_layer__DOT__output_reg[2U];
    vlSelfRef.fc_layer__DOT__output_data_o[3U] = vlSelfRef.fc_layer__DOT__output_reg[3U];
    vlSelfRef.fc_layer__DOT__output_data_o[4U] = vlSelfRef.fc_layer__DOT__output_reg[4U];
    vlSelfRef.debug_accumulator_o = (0xffffU & (IData)(vlSelfRef.fc_layer__DOT__accumulator));
    vlSelfRef.debug_addr_counter_o = ((0x3f8U & ((IData)(vlSelfRef.fc_layer__DOT__input_counter) 
                                                 << 3U)) 
                                      | (7U & (IData)(vlSelfRef.fc_layer__DOT__output_counter)));
    vlSelfRef.fc_layer__DOT__input_counter_next = vlSelfRef.fc_layer__DOT__input_counter;
    vlSelfRef.fc_layer__DOT__output_counter_next = vlSelfRef.fc_layer__DOT__output_counter;
    vlSelfRef.fc_layer__DOT__next_state = vlSelfRef.fc_layer__DOT__current_state;
    vlSelfRef.debug_state_o = (((IData)(vlSelfRef.fc_layer__DOT__current_state) 
                                << 1U) | (IData)(vlSelfRef.mode_i));
    vlSelfRef.fc_layer__DOT__ready_o = ((0U == (IData)(vlSelfRef.fc_layer__DOT__current_state)) 
                                        | ((~ (IData)(vlSelfRef.mode_i)) 
                                           & ((1U == (IData)(vlSelfRef.fc_layer__DOT__current_state)) 
                                              | (2U 
                                                 == (IData)(vlSelfRef.fc_layer__DOT__current_state)))));
    vlSelfRef.fc_layer__DOT__output_reg_next[0U] = 
        vlSelfRef.fc_layer__DOT__output_reg[0U];
    vlSelfRef.fc_layer__DOT__output_reg_next[1U] = 
        vlSelfRef.fc_layer__DOT__output_reg[1U];
    vlSelfRef.fc_layer__DOT__output_reg_next[2U] = 
        vlSelfRef.fc_layer__DOT__output_reg[2U];
    vlSelfRef.fc_layer__DOT__output_reg_next[3U] = 
        vlSelfRef.fc_layer__DOT__output_reg[3U];
    vlSelfRef.fc_layer__DOT__output_reg_next[4U] = 
        vlSelfRef.fc_layer__DOT__output_reg[4U];
    vlSelfRef.fc_layer__DOT__final_result = 0U;
    vlSelfRef.fc_layer__DOT__overflow_flag = 0U;
    vlSelfRef.fc_layer__DOT__underflow_flag = 0U;
    vlSelfRef.fc_layer__DOT__computation_done = 0U;
    vlSelfRef.fc_layer__DOT__accumulator_next = vlSelfRef.fc_layer__DOT__accumulator;
    vlSelfRef.fc_layer__DOT__mult_result_full = 0U;
    vlSelfRef.fc_layer__DOT__mult_result = 0U;
    if ((4U & (IData)(vlSelfRef.fc_layer__DOT__current_state))) {
        if ((1U & (~ ((IData)(vlSelfRef.fc_layer__DOT__current_state) 
                      >> 1U)))) {
            if ((1U & (~ (IData)(vlSelfRef.fc_layer__DOT__current_state)))) {
                if ((0x63U != (IData)(vlSelfRef.fc_layer__DOT__input_counter))) {
                    vlSelfRef.fc_layer__DOT__input_counter_next 
                        = (0x3ffU & ((IData)(1U) + (IData)(vlSelfRef.fc_layer__DOT__input_counter)));
                }
                vlSelfRef.fc_layer__DOT__mult_result_full 
                    = VL_MULS_III(32, VL_EXTENDS_II(32,16, 
                                                    ((0x63fU 
                                                      >= 
                                                      (0x7ffU 
                                                       & VL_SHIFTL_III(11,32,32, (IData)(vlSelfRef.fc_layer__DOT__input_counter), 4U)))
                                                      ? 
                                                     (0xffffU 
                                                      & (((0U 
                                                           == 
                                                           (0x1fU 
                                                            & VL_SHIFTL_III(11,32,32, (IData)(vlSelfRef.fc_layer__DOT__input_counter), 4U)))
                                                           ? 0U
                                                           : 
                                                          (vlSelfRef.fc_layer__DOT__input_reg[
                                                           (((IData)(0xfU) 
                                                             + 
                                                             (0x7ffU 
                                                              & VL_SHIFTL_III(11,32,32, (IData)(vlSelfRef.fc_layer__DOT__input_counter), 4U))) 
                                                            >> 5U)] 
                                                           << 
                                                           ((IData)(0x20U) 
                                                            - 
                                                            (0x1fU 
                                                             & VL_SHIFTL_III(11,32,32, (IData)(vlSelfRef.fc_layer__DOT__input_counter), 4U))))) 
                                                         | (vlSelfRef.fc_layer__DOT__input_reg[
                                                            (0x3fU 
                                                             & (VL_SHIFTL_III(11,32,32, (IData)(vlSelfRef.fc_layer__DOT__input_counter), 4U) 
                                                                >> 5U))] 
                                                            >> 
                                                            (0x1fU 
                                                             & VL_SHIFTL_III(11,32,32, (IData)(vlSelfRef.fc_layer__DOT__input_counter), 4U)))))
                                                      : 0U)), 
                                  VL_EXTENDS_II(32,16, 
                                                ((0x3e7fU 
                                                  >= 
                                                  (0x3fffU 
                                                   & (((IData)(0xa0U) 
                                                       * (IData)(vlSelfRef.fc_layer__DOT__input_counter)) 
                                                      + 
                                                      (0xffU 
                                                       & VL_SHIFTL_III(8,32,32, (IData)(vlSelfRef.fc_layer__DOT__output_counter), 4U)))))
                                                  ? 
                                                 (0xffffU 
                                                  & (((0U 
                                                       == 
                                                       (0x1fU 
                                                        & (((IData)(0xa0U) 
                                                            * (IData)(vlSelfRef.fc_layer__DOT__input_counter)) 
                                                           + 
                                                           (0xffU 
                                                            & VL_SHIFTL_III(8,32,32, (IData)(vlSelfRef.fc_layer__DOT__output_counter), 4U)))))
                                                       ? 0U
                                                       : 
                                                      (vlSelfRef.fc_layer__DOT__weight_memory[
                                                       (((IData)(0xfU) 
                                                         + 
                                                         (0x3fffU 
                                                          & (((IData)(0xa0U) 
                                                              * (IData)(vlSelfRef.fc_layer__DOT__input_counter)) 
                                                             + 
                                                             (0xffU 
                                                              & VL_SHIFTL_III(8,32,32, (IData)(vlSelfRef.fc_layer__DOT__output_counter), 4U))))) 
                                                        >> 5U)] 
                                                       << 
                                                       ((IData)(0x20U) 
                                                        - 
                                                        (0x1fU 
                                                         & (((IData)(0xa0U) 
                                                             * (IData)(vlSelfRef.fc_layer__DOT__input_counter)) 
                                                            + 
                                                            (0xffU 
                                                             & VL_SHIFTL_III(8,32,32, (IData)(vlSelfRef.fc_layer__DOT__output_counter), 4U))))))) 
                                                     | (vlSelfRef.fc_layer__DOT__weight_memory[
                                                        (0x1ffU 
                                                         & ((((IData)(0xa0U) 
                                                              * (IData)(vlSelfRef.fc_layer__DOT__input_counter)) 
                                                             + 
                                                             (0xffU 
                                                              & VL_SHIFTL_III(8,32,32, (IData)(vlSelfRef.fc_layer__DOT__output_counter), 4U))) 
                                                            >> 5U))] 
                                                        >> 
                                                        (0x1fU 
                                                         & (((IData)(0xa0U) 
                                                             * (IData)(vlSelfRef.fc_layer__DOT__input_counter)) 
                                                            + 
                                                            (0xffU 
                                                             & VL_SHIFTL_III(8,32,32, (IData)(vlSelfRef.fc_layer__DOT__output_counter), 4U)))))))
                                                  : 0U)));
                vlSelfRef.fc_layer__DOT__mult_result 
                    = (0xffffU & (vlSelfRef.fc_layer__DOT__mult_result_full 
                                  >> 8U));
                vlSelfRef.fc_layer__DOT__accumulator_next 
                    = (0x3ffffffffffULL & (vlSelfRef.fc_layer__DOT__accumulator 
                                           + (((QData)((IData)(
                                                               (0x3ffffffU 
                                                                & (- (IData)(
                                                                             (1U 
                                                                              & ((IData)(vlSelfRef.fc_layer__DOT__mult_result) 
                                                                                >> 0xfU))))))) 
                                               << 0x10U) 
                                              | (QData)((IData)(vlSelfRef.fc_layer__DOT__mult_result)))));
            }
            if ((1U & (IData)(vlSelfRef.fc_layer__DOT__current_state))) {
                if ((9U == (IData)(vlSelfRef.fc_layer__DOT__output_counter))) {
                    vlSelfRef.fc_layer__DOT__output_counter_next = 0U;
                    vlSelfRef.fc_layer__DOT__computation_done = 1U;
                } else {
                    vlSelfRef.fc_layer__DOT__output_counter_next 
                        = (0x3ffU & ((IData)(1U) + (IData)(vlSelfRef.fc_layer__DOT__output_counter)));
                }
                vlSelfRef.fc_layer__DOT__final_result 
                    = (0xffffU & (IData)(vlSelfRef.fc_layer__DOT__accumulator));
                vlSelfRef.fc_layer__DOT____Vlvbound_hc325c5e8__0 
                    = vlSelfRef.fc_layer__DOT__final_result;
                if ((0x9fU >= (0xffU & VL_SHIFTL_III(8,32,32, (IData)(vlSelfRef.fc_layer__DOT__output_counter), 4U)))) {
                    VL_ASSIGNSEL_WI(160,16,(0xffU & 
                                            VL_SHIFTL_III(8,32,32, (IData)(vlSelfRef.fc_layer__DOT__output_counter), 4U)), vlSelfRef.fc_layer__DOT__output_reg_next, vlSelfRef.fc_layer__DOT____Vlvbound_hc325c5e8__0);
                }
                vlSelfRef.fc_layer__DOT__overflow_flag = 0U;
                vlSelfRef.fc_layer__DOT__underflow_flag = 0U;
            }
        }
        if ((2U & (IData)(vlSelfRef.fc_layer__DOT__current_state))) {
            vlSelfRef.fc_layer__DOT__next_state = 0U;
        } else if ((1U & (IData)(vlSelfRef.fc_layer__DOT__current_state))) {
            vlSelfRef.fc_layer__DOT__next_state = (
                                                   (9U 
                                                    == (IData)(vlSelfRef.fc_layer__DOT__output_counter))
                                                    ? 0U
                                                    : 3U);
        } else if ((0x63U == (IData)(vlSelfRef.fc_layer__DOT__input_counter))) {
            vlSelfRef.fc_layer__DOT__next_state = 5U;
        }
    } else if ((2U & (IData)(vlSelfRef.fc_layer__DOT__current_state))) {
        if ((1U & (IData)(vlSelfRef.fc_layer__DOT__current_state))) {
            vlSelfRef.fc_layer__DOT__input_counter_next = 0U;
            vlSelfRef.fc_layer__DOT__next_state = 4U;
            vlSelfRef.fc_layer__DOT__accumulator_next 
                = (((QData)((IData)((0x3ffffffU & (- (IData)(
                                                             ((0x9fU 
                                                               >= 
                                                               (0xffU 
                                                                & ((IData)(0xfU) 
                                                                   + 
                                                                   VL_SHIFTL_III(8,32,32, (IData)(vlSelfRef.fc_layer__DOT__output_counter), 4U)))) 
                                                              && (1U 
                                                                  & (vlSelfRef.fc_layer__DOT__bias_memory[
                                                                     (7U 
                                                                      & (((IData)(0xfU) 
                                                                          + 
                                                                          VL_SHIFTL_III(8,32,32, (IData)(vlSelfRef.fc_layer__DOT__output_counter), 4U)) 
                                                                         >> 5U))] 
                                                                     >> 
                                                                     (0x1fU 
                                                                      & ((IData)(0xfU) 
                                                                         + 
                                                                         VL_SHIFTL_III(8,32,32, (IData)(vlSelfRef.fc_layer__DOT__output_counter), 4U))))))))))) 
                    << 0x10U) | (QData)((IData)(((0x9fU 
                                                  >= 
                                                  (0xffU 
                                                   & VL_SHIFTL_III(8,32,32, (IData)(vlSelfRef.fc_layer__DOT__output_counter), 4U)))
                                                  ? 
                                                 (0xffffU 
                                                  & (((0U 
                                                       == 
                                                       (0x1fU 
                                                        & VL_SHIFTL_III(8,32,32, (IData)(vlSelfRef.fc_layer__DOT__output_counter), 4U)))
                                                       ? 0U
                                                       : 
                                                      (vlSelfRef.fc_layer__DOT__bias_memory[
                                                       (((IData)(0xfU) 
                                                         + 
                                                         (0xffU 
                                                          & VL_SHIFTL_III(8,32,32, (IData)(vlSelfRef.fc_layer__DOT__output_counter), 4U))) 
                                                        >> 5U)] 
                                                       << 
                                                       ((IData)(0x20U) 
                                                        - 
                                                        (0x1fU 
                                                         & VL_SHIFTL_III(8,32,32, (IData)(vlSelfRef.fc_layer__DOT__output_counter), 4U))))) 
                                                     | (vlSelfRef.fc_layer__DOT__bias_memory[
                                                        (7U 
                                                         & (VL_SHIFTL_III(8,32,32, (IData)(vlSelfRef.fc_layer__DOT__output_counter), 4U) 
                                                            >> 5U))] 
                                                        >> 
                                                        (0x1fU 
                                                         & VL_SHIFTL_III(8,32,32, (IData)(vlSelfRef.fc_layer__DOT__output_counter), 4U)))))
                                                  : 0U))));
        } else if (vlSelfRef.mode_i) {
            vlSelfRef.fc_layer__DOT__input_counter_next = 0U;
            vlSelfRef.fc_layer__DOT__next_state = 3U;
            vlSelfRef.fc_layer__DOT__accumulator_next = 0ULL;
        }
        if ((1U & (~ (IData)(vlSelfRef.fc_layer__DOT__current_state)))) {
            if (vlSelfRef.mode_i) {
                vlSelfRef.fc_layer__DOT__output_counter_next = 0U;
            }
        }
    } else if ((1U & (IData)(vlSelfRef.fc_layer__DOT__current_state))) {
        if (vlSelfRef.mode_i) {
            vlSelfRef.fc_layer__DOT__input_counter_next = 0U;
            vlSelfRef.fc_layer__DOT__output_counter_next = 0U;
            vlSelfRef.fc_layer__DOT__next_state = 3U;
            vlSelfRef.fc_layer__DOT__accumulator_next = 0ULL;
        }
    } else if (vlSelfRef.valid_i) {
        if (vlSelfRef.mode_i) {
            vlSelfRef.fc_layer__DOT__input_counter_next = 0U;
            vlSelfRef.fc_layer__DOT__output_counter_next = 0U;
            vlSelfRef.fc_layer__DOT__next_state = 3U;
            vlSelfRef.fc_layer__DOT__accumulator_next = 0ULL;
        } else {
            vlSelfRef.fc_layer__DOT__next_state = 1U;
        }
    }
    vlSelfRef.fc_layer__DOT__debug_accumulator_o = vlSelfRef.debug_accumulator_o;
    vlSelfRef.fc_layer__DOT__debug_addr_counter_o = vlSelfRef.debug_addr_counter_o;
    vlSelfRef.fc_layer__DOT__debug_state_o = vlSelfRef.debug_state_o;
    vlSelfRef.ready_o = vlSelfRef.fc_layer__DOT__ready_o;
    vlSelfRef.debug_flags_o = ((((IData)(vlSelfRef.fc_layer__DOT__computation_done) 
                                 << 3U) | ((IData)(vlSelfRef.fc_layer__DOT__overflow_flag) 
                                           << 2U)) 
                               | (((IData)(vlSelfRef.fc_layer__DOT__underflow_flag) 
                                   << 1U) | (IData)(vlSelfRef.fc_layer__DOT__valid_o)));
    vlSelfRef.fc_layer__DOT__debug_flags_o = vlSelfRef.debug_flags_o;
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
            VL_FATAL_MT("/home/yanggl/code/BICSdifftest/examples/fc_layer/rtl/fc_layer.sv", 12, "", "Input combinational region did not converge.");
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
            VL_FATAL_MT("/home/yanggl/code/BICSdifftest/examples/fc_layer/rtl/fc_layer.sv", 12, "", "NBA region did not converge.");
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
                VL_FATAL_MT("/home/yanggl/code/BICSdifftest/examples/fc_layer/rtl/fc_layer.sv", 12, "", "Active region did not converge.");
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
    if (VL_UNLIKELY(((vlSelfRef.mode_i & 0xfeU)))) {
        Verilated::overWidthError("mode_i");}
    if (VL_UNLIKELY(((vlSelfRef.valid_i & 0xfeU)))) {
        Verilated::overWidthError("valid_i");}
    if (VL_UNLIKELY(((vlSelfRef.weight_addr_i & 0xfc00U)))) {
        Verilated::overWidthError("weight_addr_i");}
    if (VL_UNLIKELY(((vlSelfRef.weight_we_i & 0xfeU)))) {
        Verilated::overWidthError("weight_we_i");}
    if (VL_UNLIKELY(((vlSelfRef.bias_addr_i & 0xfc00U)))) {
        Verilated::overWidthError("bias_addr_i");}
    if (VL_UNLIKELY(((vlSelfRef.bias_we_i & 0xfeU)))) {
        Verilated::overWidthError("bias_we_i");}
}
#endif  // VL_DEBUG
