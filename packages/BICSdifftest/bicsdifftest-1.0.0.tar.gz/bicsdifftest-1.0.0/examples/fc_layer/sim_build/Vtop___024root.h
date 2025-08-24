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
    // Anonymous structures to workaround compiler member-count bugs
    struct {
        VL_IN8(clk,0,0);
        VL_IN8(rst_n,0,0);
        VL_IN8(mode_i,0,0);
        VL_IN8(valid_i,0,0);
        VL_OUT8(ready_o,0,0);
        VL_IN8(weight_we_i,0,0);
        VL_IN8(bias_we_i,0,0);
        VL_OUT8(valid_o,0,0);
        VL_OUT8(debug_flags_o,3,0);
        CData/*0:0*/ fc_layer__DOT__clk;
        CData/*0:0*/ fc_layer__DOT__rst_n;
        CData/*0:0*/ fc_layer__DOT__mode_i;
        CData/*0:0*/ fc_layer__DOT__valid_i;
        CData/*0:0*/ fc_layer__DOT__ready_o;
        CData/*0:0*/ fc_layer__DOT__weight_we_i;
        CData/*0:0*/ fc_layer__DOT__bias_we_i;
        CData/*0:0*/ fc_layer__DOT__valid_o;
        CData/*3:0*/ fc_layer__DOT__debug_flags_o;
        CData/*2:0*/ fc_layer__DOT__current_state;
        CData/*2:0*/ fc_layer__DOT__next_state;
        CData/*0:0*/ fc_layer__DOT__computation_done;
        CData/*0:0*/ fc_layer__DOT__weight_loading_done;
        CData/*0:0*/ fc_layer__DOT__bias_loading_done;
        CData/*0:0*/ fc_layer__DOT__overflow_flag;
        CData/*0:0*/ fc_layer__DOT__underflow_flag;
        CData/*6:0*/ fc_layer__DOT__unnamedblk4__DOT__input_idx;
        CData/*3:0*/ fc_layer__DOT__unnamedblk4__DOT__output_idx;
        CData/*0:0*/ __VstlFirstIteration;
        CData/*0:0*/ __VicoFirstIteration;
        CData/*0:0*/ __Vtrigprevexpr___TOP__clk__0;
        CData/*0:0*/ __Vtrigprevexpr___TOP__rst_n__0;
        CData/*0:0*/ __VactContinue;
        VL_IN16(weight_addr_i,9,0);
        VL_IN16(weight_data_i,15,0);
        VL_INW(input_data_i,1599,0,50);
        VL_IN16(bias_addr_i,9,0);
        VL_IN16(bias_data_i,15,0);
        VL_OUTW(output_data_o,159,0,5);
        VL_OUT16(debug_accumulator_o,15,0);
        VL_OUT16(debug_addr_counter_o,9,0);
        SData/*9:0*/ fc_layer__DOT__weight_addr_i;
        SData/*15:0*/ fc_layer__DOT__weight_data_i;
        VlWide<50>/*1599:0*/ fc_layer__DOT__input_data_i;
        SData/*9:0*/ fc_layer__DOT__bias_addr_i;
        SData/*15:0*/ fc_layer__DOT__bias_data_i;
        VlWide<5>/*159:0*/ fc_layer__DOT__output_data_o;
        SData/*15:0*/ fc_layer__DOT__debug_accumulator_o;
        SData/*9:0*/ fc_layer__DOT__debug_addr_counter_o;
        VlWide<500>/*15999:0*/ fc_layer__DOT__weight_memory;
        VlWide<5>/*159:0*/ fc_layer__DOT__bias_memory;
        VlWide<50>/*1599:0*/ fc_layer__DOT__input_reg;
        VlWide<5>/*159:0*/ fc_layer__DOT__output_reg;
        VlWide<5>/*159:0*/ fc_layer__DOT__output_reg_next;
        SData/*9:0*/ fc_layer__DOT__input_counter;
        SData/*9:0*/ fc_layer__DOT__output_counter;
        SData/*9:0*/ fc_layer__DOT__input_counter_next;
        SData/*9:0*/ fc_layer__DOT__output_counter_next;
        SData/*15:0*/ fc_layer__DOT__mult_result;
        SData/*15:0*/ fc_layer__DOT__final_result;
        SData/*15:0*/ fc_layer__DOT____Vlvbound_h8449f1d8__0;
        SData/*15:0*/ fc_layer__DOT____Vlvbound_h92854779__0;
        SData/*15:0*/ fc_layer__DOT____Vlvbound_hc62066ac__0;
        SData/*15:0*/ fc_layer__DOT____Vlvbound_hc325c5e8__0;
        VL_OUT(debug_state_o,31,0);
    };
    struct {
        IData/*31:0*/ fc_layer__DOT__debug_state_o;
        IData/*31:0*/ fc_layer__DOT__mult_result_full;
        IData/*31:0*/ fc_layer__DOT__unnamedblk1__DOT__i;
        IData/*31:0*/ fc_layer__DOT__unnamedblk1__DOT__unnamedblk2__DOT__j;
        IData/*31:0*/ fc_layer__DOT__unnamedblk3__DOT__j;
        IData/*31:0*/ __VactIterCount;
        QData/*41:0*/ fc_layer__DOT__accumulator;
        QData/*41:0*/ fc_layer__DOT__accumulator_next;
    };
    VlTriggerVec<1> __VstlTriggered;
    VlTriggerVec<1> __VicoTriggered;
    VlTriggerVec<2> __VactTriggered;
    VlTriggerVec<2> __VnbaTriggered;

    // INTERNAL VARIABLES
    Vtop__Syms* const vlSymsp;

    // PARAMETERS
    static constexpr IData/*31:0*/ fc_layer__DOT__INPUT_SIZE = 0x00000064U;
    static constexpr IData/*31:0*/ fc_layer__DOT__OUTPUT_SIZE = 0x0000000aU;
    static constexpr IData/*31:0*/ fc_layer__DOT__DATA_WIDTH = 0x00000010U;
    static constexpr IData/*31:0*/ fc_layer__DOT__FRAC_BITS = 8U;
    static constexpr IData/*31:0*/ fc_layer__DOT__WEIGHT_WIDTH = 0x00000010U;
    static constexpr IData/*31:0*/ fc_layer__DOT__ADDR_WIDTH = 0x0000000aU;

    // CONSTRUCTORS
    Vtop___024root(Vtop__Syms* symsp, const char* v__name);
    ~Vtop___024root();
    VL_UNCOPYABLE(Vtop___024root);

    // INTERNAL METHODS
    void __Vconfigure(bool first);
};


#endif  // guard
