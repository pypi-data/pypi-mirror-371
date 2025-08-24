// Verilated -*- C++ -*-
// DESCRIPTION: Verilator output: Design implementation internals
// See Vtop.h for the primary calling header

#include "Vtop__pch.h"
#include "Vtop___024root.h"

VL_ATTR_COLD void Vtop___024root___eval_static(Vtop___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtop___024root___eval_static\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.__Vtrigprevexpr___TOP__clk__0 = vlSelfRef.clk;
    vlSelfRef.__Vtrigprevexpr___TOP__rst_n__0 = vlSelfRef.rst_n;
}

VL_ATTR_COLD void Vtop___024root___eval_initial__TOP(Vtop___024root* vlSelf);

VL_ATTR_COLD void Vtop___024root___eval_initial(Vtop___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtop___024root___eval_initial\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    Vtop___024root___eval_initial__TOP(vlSelf);
}

VL_ATTR_COLD void Vtop___024root___eval_initial__TOP(Vtop___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtop___024root___eval_initial__TOP\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.fc_layer__DOT__weight_loading_done = 0U;
    vlSelfRef.fc_layer__DOT__bias_loading_done = 0U;
}

VL_ATTR_COLD void Vtop___024root___eval_final(Vtop___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtop___024root___eval_final\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
}

#ifdef VL_DEBUG
VL_ATTR_COLD void Vtop___024root___dump_triggers__stl(Vtop___024root* vlSelf);
#endif  // VL_DEBUG
VL_ATTR_COLD bool Vtop___024root___eval_phase__stl(Vtop___024root* vlSelf);

VL_ATTR_COLD void Vtop___024root___eval_settle(Vtop___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtop___024root___eval_settle\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Init
    IData/*31:0*/ __VstlIterCount;
    CData/*0:0*/ __VstlContinue;
    // Body
    __VstlIterCount = 0U;
    vlSelfRef.__VstlFirstIteration = 1U;
    __VstlContinue = 1U;
    while (__VstlContinue) {
        if (VL_UNLIKELY(((0x64U < __VstlIterCount)))) {
#ifdef VL_DEBUG
            Vtop___024root___dump_triggers__stl(vlSelf);
#endif
            VL_FATAL_MT("/home/yanggl/code/BICSdifftest/examples/fc_layer/rtl/fc_layer.sv", 12, "", "Settle region did not converge.");
        }
        __VstlIterCount = ((IData)(1U) + __VstlIterCount);
        __VstlContinue = 0U;
        if (Vtop___024root___eval_phase__stl(vlSelf)) {
            __VstlContinue = 1U;
        }
        vlSelfRef.__VstlFirstIteration = 0U;
    }
}

#ifdef VL_DEBUG
VL_ATTR_COLD void Vtop___024root___dump_triggers__stl(Vtop___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtop___024root___dump_triggers__stl\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    if ((1U & (~ vlSelfRef.__VstlTriggered.any()))) {
        VL_DBG_MSGF("         No triggers active\n");
    }
    if ((1ULL & vlSelfRef.__VstlTriggered.word(0U))) {
        VL_DBG_MSGF("         'stl' region trigger index 0 is active: Internal 'stl' trigger - first iteration\n");
    }
}
#endif  // VL_DEBUG

void Vtop___024root___ico_sequent__TOP__0(Vtop___024root* vlSelf);

VL_ATTR_COLD void Vtop___024root___eval_stl(Vtop___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtop___024root___eval_stl\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    if ((1ULL & vlSelfRef.__VstlTriggered.word(0U))) {
        Vtop___024root___ico_sequent__TOP__0(vlSelf);
    }
}

VL_ATTR_COLD void Vtop___024root___eval_triggers__stl(Vtop___024root* vlSelf);

VL_ATTR_COLD bool Vtop___024root___eval_phase__stl(Vtop___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtop___024root___eval_phase__stl\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Init
    CData/*0:0*/ __VstlExecute;
    // Body
    Vtop___024root___eval_triggers__stl(vlSelf);
    __VstlExecute = vlSelfRef.__VstlTriggered.any();
    if (__VstlExecute) {
        Vtop___024root___eval_stl(vlSelf);
    }
    return (__VstlExecute);
}

#ifdef VL_DEBUG
VL_ATTR_COLD void Vtop___024root___dump_triggers__ico(Vtop___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtop___024root___dump_triggers__ico\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    if ((1U & (~ vlSelfRef.__VicoTriggered.any()))) {
        VL_DBG_MSGF("         No triggers active\n");
    }
    if ((1ULL & vlSelfRef.__VicoTriggered.word(0U))) {
        VL_DBG_MSGF("         'ico' region trigger index 0 is active: Internal 'ico' trigger - first iteration\n");
    }
}
#endif  // VL_DEBUG

#ifdef VL_DEBUG
VL_ATTR_COLD void Vtop___024root___dump_triggers__act(Vtop___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtop___024root___dump_triggers__act\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    if ((1U & (~ vlSelfRef.__VactTriggered.any()))) {
        VL_DBG_MSGF("         No triggers active\n");
    }
    if ((1ULL & vlSelfRef.__VactTriggered.word(0U))) {
        VL_DBG_MSGF("         'act' region trigger index 0 is active: @(posedge clk)\n");
    }
    if ((2ULL & vlSelfRef.__VactTriggered.word(0U))) {
        VL_DBG_MSGF("         'act' region trigger index 1 is active: @(negedge rst_n)\n");
    }
}
#endif  // VL_DEBUG

#ifdef VL_DEBUG
VL_ATTR_COLD void Vtop___024root___dump_triggers__nba(Vtop___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtop___024root___dump_triggers__nba\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    if ((1U & (~ vlSelfRef.__VnbaTriggered.any()))) {
        VL_DBG_MSGF("         No triggers active\n");
    }
    if ((1ULL & vlSelfRef.__VnbaTriggered.word(0U))) {
        VL_DBG_MSGF("         'nba' region trigger index 0 is active: @(posedge clk)\n");
    }
    if ((2ULL & vlSelfRef.__VnbaTriggered.word(0U))) {
        VL_DBG_MSGF("         'nba' region trigger index 1 is active: @(negedge rst_n)\n");
    }
}
#endif  // VL_DEBUG

VL_ATTR_COLD void Vtop___024root___ctor_var_reset(Vtop___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtop___024root___ctor_var_reset\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelf->clk = 0;
    vlSelf->rst_n = 0;
    vlSelf->mode_i = 0;
    vlSelf->valid_i = 0;
    vlSelf->ready_o = 0;
    vlSelf->weight_addr_i = 0;
    vlSelf->weight_data_i = 0;
    vlSelf->weight_we_i = 0;
    VL_ZERO_RESET_W(1600, vlSelf->input_data_i);
    vlSelf->bias_addr_i = 0;
    vlSelf->bias_data_i = 0;
    vlSelf->bias_we_i = 0;
    VL_ZERO_RESET_W(160, vlSelf->output_data_o);
    vlSelf->valid_o = 0;
    vlSelf->debug_state_o = 0;
    vlSelf->debug_accumulator_o = 0;
    vlSelf->debug_addr_counter_o = 0;
    vlSelf->debug_flags_o = 0;
    vlSelf->fc_layer__DOT__clk = 0;
    vlSelf->fc_layer__DOT__rst_n = 0;
    vlSelf->fc_layer__DOT__mode_i = 0;
    vlSelf->fc_layer__DOT__valid_i = 0;
    vlSelf->fc_layer__DOT__ready_o = 0;
    vlSelf->fc_layer__DOT__weight_addr_i = 0;
    vlSelf->fc_layer__DOT__weight_data_i = 0;
    vlSelf->fc_layer__DOT__weight_we_i = 0;
    VL_ZERO_RESET_W(1600, vlSelf->fc_layer__DOT__input_data_i);
    vlSelf->fc_layer__DOT__bias_addr_i = 0;
    vlSelf->fc_layer__DOT__bias_data_i = 0;
    vlSelf->fc_layer__DOT__bias_we_i = 0;
    VL_ZERO_RESET_W(160, vlSelf->fc_layer__DOT__output_data_o);
    vlSelf->fc_layer__DOT__valid_o = 0;
    vlSelf->fc_layer__DOT__debug_state_o = 0;
    vlSelf->fc_layer__DOT__debug_accumulator_o = 0;
    vlSelf->fc_layer__DOT__debug_addr_counter_o = 0;
    vlSelf->fc_layer__DOT__debug_flags_o = 0;
    VL_ZERO_RESET_W(16000, vlSelf->fc_layer__DOT__weight_memory);
    VL_ZERO_RESET_W(160, vlSelf->fc_layer__DOT__bias_memory);
    VL_ZERO_RESET_W(1600, vlSelf->fc_layer__DOT__input_reg);
    VL_ZERO_RESET_W(160, vlSelf->fc_layer__DOT__output_reg);
    VL_ZERO_RESET_W(160, vlSelf->fc_layer__DOT__output_reg_next);
    vlSelf->fc_layer__DOT__current_state = 0;
    vlSelf->fc_layer__DOT__next_state = 0;
    vlSelf->fc_layer__DOT__input_counter = 0;
    vlSelf->fc_layer__DOT__output_counter = 0;
    vlSelf->fc_layer__DOT__input_counter_next = 0;
    vlSelf->fc_layer__DOT__output_counter_next = 0;
    vlSelf->fc_layer__DOT__mult_result_full = 0;
    vlSelf->fc_layer__DOT__mult_result = 0;
    vlSelf->fc_layer__DOT__accumulator = 0;
    vlSelf->fc_layer__DOT__accumulator_next = 0;
    vlSelf->fc_layer__DOT__final_result = 0;
    vlSelf->fc_layer__DOT__computation_done = 0;
    vlSelf->fc_layer__DOT__weight_loading_done = 0;
    vlSelf->fc_layer__DOT__bias_loading_done = 0;
    vlSelf->fc_layer__DOT__overflow_flag = 0;
    vlSelf->fc_layer__DOT__underflow_flag = 0;
    vlSelf->fc_layer__DOT__unnamedblk4__DOT__input_idx = 0;
    vlSelf->fc_layer__DOT__unnamedblk4__DOT__output_idx = 0;
    vlSelf->fc_layer__DOT__unnamedblk1__DOT__i = 0;
    vlSelf->fc_layer__DOT__unnamedblk1__DOT__unnamedblk2__DOT__j = 0;
    vlSelf->fc_layer__DOT__unnamedblk3__DOT__j = 0;
    vlSelf->fc_layer__DOT____Vlvbound_h8449f1d8__0 = 0;
    vlSelf->fc_layer__DOT____Vlvbound_h92854779__0 = 0;
    vlSelf->fc_layer__DOT____Vlvbound_hc62066ac__0 = 0;
    vlSelf->fc_layer__DOT____Vlvbound_hc325c5e8__0 = 0;
    vlSelf->__Vtrigprevexpr___TOP__clk__0 = 0;
    vlSelf->__Vtrigprevexpr___TOP__rst_n__0 = 0;
}
