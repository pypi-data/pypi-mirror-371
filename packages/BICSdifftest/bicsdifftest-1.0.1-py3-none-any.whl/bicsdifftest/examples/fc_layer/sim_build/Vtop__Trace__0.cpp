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
    bufp->chgBit(oldp+2,(vlSelfRef.mode_i));
    bufp->chgBit(oldp+3,(vlSelfRef.valid_i));
    bufp->chgBit(oldp+4,(vlSelfRef.ready_o));
    bufp->chgSData(oldp+5,(vlSelfRef.weight_addr_i),10);
    bufp->chgSData(oldp+6,(vlSelfRef.weight_data_i),16);
    bufp->chgBit(oldp+7,(vlSelfRef.weight_we_i));
    bufp->chgSData(oldp+8,((0xffffU & vlSelfRef.input_data_i[0U])),16);
    bufp->chgSData(oldp+9,((vlSelfRef.input_data_i[0U] 
                            >> 0x10U)),16);
    bufp->chgSData(oldp+10,((0xffffU & vlSelfRef.input_data_i[1U])),16);
    bufp->chgSData(oldp+11,((vlSelfRef.input_data_i[1U] 
                             >> 0x10U)),16);
    bufp->chgSData(oldp+12,((0xffffU & vlSelfRef.input_data_i[2U])),16);
    bufp->chgSData(oldp+13,((vlSelfRef.input_data_i[2U] 
                             >> 0x10U)),16);
    bufp->chgSData(oldp+14,((0xffffU & vlSelfRef.input_data_i[3U])),16);
    bufp->chgSData(oldp+15,((vlSelfRef.input_data_i[3U] 
                             >> 0x10U)),16);
    bufp->chgSData(oldp+16,((0xffffU & vlSelfRef.input_data_i[4U])),16);
    bufp->chgSData(oldp+17,((vlSelfRef.input_data_i[4U] 
                             >> 0x10U)),16);
    bufp->chgSData(oldp+18,((0xffffU & vlSelfRef.input_data_i[5U])),16);
    bufp->chgSData(oldp+19,((vlSelfRef.input_data_i[5U] 
                             >> 0x10U)),16);
    bufp->chgSData(oldp+20,((0xffffU & vlSelfRef.input_data_i[6U])),16);
    bufp->chgSData(oldp+21,((vlSelfRef.input_data_i[6U] 
                             >> 0x10U)),16);
    bufp->chgSData(oldp+22,((0xffffU & vlSelfRef.input_data_i[7U])),16);
    bufp->chgSData(oldp+23,((vlSelfRef.input_data_i[7U] 
                             >> 0x10U)),16);
    bufp->chgSData(oldp+24,((0xffffU & vlSelfRef.input_data_i[8U])),16);
    bufp->chgSData(oldp+25,((vlSelfRef.input_data_i[8U] 
                             >> 0x10U)),16);
    bufp->chgSData(oldp+26,((0xffffU & vlSelfRef.input_data_i[9U])),16);
    bufp->chgSData(oldp+27,((vlSelfRef.input_data_i[9U] 
                             >> 0x10U)),16);
    bufp->chgSData(oldp+28,((0xffffU & vlSelfRef.input_data_i[0xaU])),16);
    bufp->chgSData(oldp+29,((vlSelfRef.input_data_i[0xaU] 
                             >> 0x10U)),16);
    bufp->chgSData(oldp+30,((0xffffU & vlSelfRef.input_data_i[0xbU])),16);
    bufp->chgSData(oldp+31,((vlSelfRef.input_data_i[0xbU] 
                             >> 0x10U)),16);
    bufp->chgSData(oldp+32,((0xffffU & vlSelfRef.input_data_i[0xcU])),16);
    bufp->chgSData(oldp+33,((vlSelfRef.input_data_i[0xcU] 
                             >> 0x10U)),16);
    bufp->chgSData(oldp+34,((0xffffU & vlSelfRef.input_data_i[0xdU])),16);
    bufp->chgSData(oldp+35,((vlSelfRef.input_data_i[0xdU] 
                             >> 0x10U)),16);
    bufp->chgSData(oldp+36,((0xffffU & vlSelfRef.input_data_i[0xeU])),16);
    bufp->chgSData(oldp+37,((vlSelfRef.input_data_i[0xeU] 
                             >> 0x10U)),16);
    bufp->chgSData(oldp+38,((0xffffU & vlSelfRef.input_data_i[0xfU])),16);
    bufp->chgSData(oldp+39,((vlSelfRef.input_data_i[0xfU] 
                             >> 0x10U)),16);
    bufp->chgSData(oldp+40,((0xffffU & vlSelfRef.input_data_i[0x10U])),16);
    bufp->chgSData(oldp+41,((vlSelfRef.input_data_i[0x10U] 
                             >> 0x10U)),16);
    bufp->chgSData(oldp+42,((0xffffU & vlSelfRef.input_data_i[0x11U])),16);
    bufp->chgSData(oldp+43,((vlSelfRef.input_data_i[0x11U] 
                             >> 0x10U)),16);
    bufp->chgSData(oldp+44,((0xffffU & vlSelfRef.input_data_i[0x12U])),16);
    bufp->chgSData(oldp+45,((vlSelfRef.input_data_i[0x12U] 
                             >> 0x10U)),16);
    bufp->chgSData(oldp+46,((0xffffU & vlSelfRef.input_data_i[0x13U])),16);
    bufp->chgSData(oldp+47,((vlSelfRef.input_data_i[0x13U] 
                             >> 0x10U)),16);
    bufp->chgSData(oldp+48,((0xffffU & vlSelfRef.input_data_i[0x14U])),16);
    bufp->chgSData(oldp+49,((vlSelfRef.input_data_i[0x14U] 
                             >> 0x10U)),16);
    bufp->chgSData(oldp+50,((0xffffU & vlSelfRef.input_data_i[0x15U])),16);
    bufp->chgSData(oldp+51,((vlSelfRef.input_data_i[0x15U] 
                             >> 0x10U)),16);
    bufp->chgSData(oldp+52,((0xffffU & vlSelfRef.input_data_i[0x16U])),16);
    bufp->chgSData(oldp+53,((vlSelfRef.input_data_i[0x16U] 
                             >> 0x10U)),16);
    bufp->chgSData(oldp+54,((0xffffU & vlSelfRef.input_data_i[0x17U])),16);
    bufp->chgSData(oldp+55,((vlSelfRef.input_data_i[0x17U] 
                             >> 0x10U)),16);
    bufp->chgSData(oldp+56,((0xffffU & vlSelfRef.input_data_i[0x18U])),16);
    bufp->chgSData(oldp+57,((vlSelfRef.input_data_i[0x18U] 
                             >> 0x10U)),16);
    bufp->chgSData(oldp+58,((0xffffU & vlSelfRef.input_data_i[0x19U])),16);
    bufp->chgSData(oldp+59,((vlSelfRef.input_data_i[0x19U] 
                             >> 0x10U)),16);
    bufp->chgSData(oldp+60,((0xffffU & vlSelfRef.input_data_i[0x1aU])),16);
    bufp->chgSData(oldp+61,((vlSelfRef.input_data_i[0x1aU] 
                             >> 0x10U)),16);
    bufp->chgSData(oldp+62,((0xffffU & vlSelfRef.input_data_i[0x1bU])),16);
    bufp->chgSData(oldp+63,((vlSelfRef.input_data_i[0x1bU] 
                             >> 0x10U)),16);
    bufp->chgSData(oldp+64,((0xffffU & vlSelfRef.input_data_i[0x1cU])),16);
    bufp->chgSData(oldp+65,((vlSelfRef.input_data_i[0x1cU] 
                             >> 0x10U)),16);
    bufp->chgSData(oldp+66,((0xffffU & vlSelfRef.input_data_i[0x1dU])),16);
    bufp->chgSData(oldp+67,((vlSelfRef.input_data_i[0x1dU] 
                             >> 0x10U)),16);
    bufp->chgSData(oldp+68,((0xffffU & vlSelfRef.input_data_i[0x1eU])),16);
    bufp->chgSData(oldp+69,((vlSelfRef.input_data_i[0x1eU] 
                             >> 0x10U)),16);
    bufp->chgSData(oldp+70,((0xffffU & vlSelfRef.input_data_i[0x1fU])),16);
    bufp->chgSData(oldp+71,((vlSelfRef.input_data_i[0x1fU] 
                             >> 0x10U)),16);
    bufp->chgSData(oldp+72,((0xffffU & vlSelfRef.input_data_i[0x20U])),16);
    bufp->chgSData(oldp+73,((vlSelfRef.input_data_i[0x20U] 
                             >> 0x10U)),16);
    bufp->chgSData(oldp+74,((0xffffU & vlSelfRef.input_data_i[0x21U])),16);
    bufp->chgSData(oldp+75,((vlSelfRef.input_data_i[0x21U] 
                             >> 0x10U)),16);
    bufp->chgSData(oldp+76,((0xffffU & vlSelfRef.input_data_i[0x22U])),16);
    bufp->chgSData(oldp+77,((vlSelfRef.input_data_i[0x22U] 
                             >> 0x10U)),16);
    bufp->chgSData(oldp+78,((0xffffU & vlSelfRef.input_data_i[0x23U])),16);
    bufp->chgSData(oldp+79,((vlSelfRef.input_data_i[0x23U] 
                             >> 0x10U)),16);
    bufp->chgSData(oldp+80,((0xffffU & vlSelfRef.input_data_i[0x24U])),16);
    bufp->chgSData(oldp+81,((vlSelfRef.input_data_i[0x24U] 
                             >> 0x10U)),16);
    bufp->chgSData(oldp+82,((0xffffU & vlSelfRef.input_data_i[0x25U])),16);
    bufp->chgSData(oldp+83,((vlSelfRef.input_data_i[0x25U] 
                             >> 0x10U)),16);
    bufp->chgSData(oldp+84,((0xffffU & vlSelfRef.input_data_i[0x26U])),16);
    bufp->chgSData(oldp+85,((vlSelfRef.input_data_i[0x26U] 
                             >> 0x10U)),16);
    bufp->chgSData(oldp+86,((0xffffU & vlSelfRef.input_data_i[0x27U])),16);
    bufp->chgSData(oldp+87,((vlSelfRef.input_data_i[0x27U] 
                             >> 0x10U)),16);
    bufp->chgSData(oldp+88,((0xffffU & vlSelfRef.input_data_i[0x28U])),16);
    bufp->chgSData(oldp+89,((vlSelfRef.input_data_i[0x28U] 
                             >> 0x10U)),16);
    bufp->chgSData(oldp+90,((0xffffU & vlSelfRef.input_data_i[0x29U])),16);
    bufp->chgSData(oldp+91,((vlSelfRef.input_data_i[0x29U] 
                             >> 0x10U)),16);
    bufp->chgSData(oldp+92,((0xffffU & vlSelfRef.input_data_i[0x2aU])),16);
    bufp->chgSData(oldp+93,((vlSelfRef.input_data_i[0x2aU] 
                             >> 0x10U)),16);
    bufp->chgSData(oldp+94,((0xffffU & vlSelfRef.input_data_i[0x2bU])),16);
    bufp->chgSData(oldp+95,((vlSelfRef.input_data_i[0x2bU] 
                             >> 0x10U)),16);
    bufp->chgSData(oldp+96,((0xffffU & vlSelfRef.input_data_i[0x2cU])),16);
    bufp->chgSData(oldp+97,((vlSelfRef.input_data_i[0x2cU] 
                             >> 0x10U)),16);
    bufp->chgSData(oldp+98,((0xffffU & vlSelfRef.input_data_i[0x2dU])),16);
    bufp->chgSData(oldp+99,((vlSelfRef.input_data_i[0x2dU] 
                             >> 0x10U)),16);
    bufp->chgSData(oldp+100,((0xffffU & vlSelfRef.input_data_i[0x2eU])),16);
    bufp->chgSData(oldp+101,((vlSelfRef.input_data_i[0x2eU] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+102,((0xffffU & vlSelfRef.input_data_i[0x2fU])),16);
    bufp->chgSData(oldp+103,((vlSelfRef.input_data_i[0x2fU] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+104,((0xffffU & vlSelfRef.input_data_i[0x30U])),16);
    bufp->chgSData(oldp+105,((vlSelfRef.input_data_i[0x30U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+106,((0xffffU & vlSelfRef.input_data_i[0x31U])),16);
    bufp->chgSData(oldp+107,((vlSelfRef.input_data_i[0x31U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+108,(vlSelfRef.bias_addr_i),10);
    bufp->chgSData(oldp+109,(vlSelfRef.bias_data_i),16);
    bufp->chgBit(oldp+110,(vlSelfRef.bias_we_i));
    bufp->chgSData(oldp+111,((0xffffU & vlSelfRef.output_data_o[0U])),16);
    bufp->chgSData(oldp+112,((vlSelfRef.output_data_o[0U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+113,((0xffffU & vlSelfRef.output_data_o[1U])),16);
    bufp->chgSData(oldp+114,((vlSelfRef.output_data_o[1U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+115,((0xffffU & vlSelfRef.output_data_o[2U])),16);
    bufp->chgSData(oldp+116,((vlSelfRef.output_data_o[2U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+117,((0xffffU & vlSelfRef.output_data_o[3U])),16);
    bufp->chgSData(oldp+118,((vlSelfRef.output_data_o[3U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+119,((0xffffU & vlSelfRef.output_data_o[4U])),16);
    bufp->chgSData(oldp+120,((vlSelfRef.output_data_o[4U] 
                              >> 0x10U)),16);
    bufp->chgBit(oldp+121,(vlSelfRef.valid_o));
    bufp->chgIData(oldp+122,(vlSelfRef.debug_state_o),32);
    bufp->chgSData(oldp+123,(vlSelfRef.debug_accumulator_o),16);
    bufp->chgSData(oldp+124,(vlSelfRef.debug_addr_counter_o),10);
    bufp->chgCData(oldp+125,(vlSelfRef.debug_flags_o),4);
    bufp->chgBit(oldp+126,(vlSelfRef.fc_layer__DOT__clk));
    bufp->chgBit(oldp+127,(vlSelfRef.fc_layer__DOT__rst_n));
    bufp->chgBit(oldp+128,(vlSelfRef.fc_layer__DOT__mode_i));
    bufp->chgBit(oldp+129,(vlSelfRef.fc_layer__DOT__valid_i));
    bufp->chgBit(oldp+130,(vlSelfRef.fc_layer__DOT__ready_o));
    bufp->chgSData(oldp+131,(vlSelfRef.fc_layer__DOT__weight_addr_i),10);
    bufp->chgSData(oldp+132,(vlSelfRef.fc_layer__DOT__weight_data_i),16);
    bufp->chgBit(oldp+133,(vlSelfRef.fc_layer__DOT__weight_we_i));
    bufp->chgSData(oldp+134,((0xffffU & vlSelfRef.fc_layer__DOT__input_data_i[0U])),16);
    bufp->chgSData(oldp+135,((vlSelfRef.fc_layer__DOT__input_data_i[0U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+136,((0xffffU & vlSelfRef.fc_layer__DOT__input_data_i[1U])),16);
    bufp->chgSData(oldp+137,((vlSelfRef.fc_layer__DOT__input_data_i[1U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+138,((0xffffU & vlSelfRef.fc_layer__DOT__input_data_i[2U])),16);
    bufp->chgSData(oldp+139,((vlSelfRef.fc_layer__DOT__input_data_i[2U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+140,((0xffffU & vlSelfRef.fc_layer__DOT__input_data_i[3U])),16);
    bufp->chgSData(oldp+141,((vlSelfRef.fc_layer__DOT__input_data_i[3U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+142,((0xffffU & vlSelfRef.fc_layer__DOT__input_data_i[4U])),16);
    bufp->chgSData(oldp+143,((vlSelfRef.fc_layer__DOT__input_data_i[4U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+144,((0xffffU & vlSelfRef.fc_layer__DOT__input_data_i[5U])),16);
    bufp->chgSData(oldp+145,((vlSelfRef.fc_layer__DOT__input_data_i[5U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+146,((0xffffU & vlSelfRef.fc_layer__DOT__input_data_i[6U])),16);
    bufp->chgSData(oldp+147,((vlSelfRef.fc_layer__DOT__input_data_i[6U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+148,((0xffffU & vlSelfRef.fc_layer__DOT__input_data_i[7U])),16);
    bufp->chgSData(oldp+149,((vlSelfRef.fc_layer__DOT__input_data_i[7U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+150,((0xffffU & vlSelfRef.fc_layer__DOT__input_data_i[8U])),16);
    bufp->chgSData(oldp+151,((vlSelfRef.fc_layer__DOT__input_data_i[8U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+152,((0xffffU & vlSelfRef.fc_layer__DOT__input_data_i[9U])),16);
    bufp->chgSData(oldp+153,((vlSelfRef.fc_layer__DOT__input_data_i[9U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+154,((0xffffU & vlSelfRef.fc_layer__DOT__input_data_i[0xaU])),16);
    bufp->chgSData(oldp+155,((vlSelfRef.fc_layer__DOT__input_data_i[0xaU] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+156,((0xffffU & vlSelfRef.fc_layer__DOT__input_data_i[0xbU])),16);
    bufp->chgSData(oldp+157,((vlSelfRef.fc_layer__DOT__input_data_i[0xbU] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+158,((0xffffU & vlSelfRef.fc_layer__DOT__input_data_i[0xcU])),16);
    bufp->chgSData(oldp+159,((vlSelfRef.fc_layer__DOT__input_data_i[0xcU] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+160,((0xffffU & vlSelfRef.fc_layer__DOT__input_data_i[0xdU])),16);
    bufp->chgSData(oldp+161,((vlSelfRef.fc_layer__DOT__input_data_i[0xdU] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+162,((0xffffU & vlSelfRef.fc_layer__DOT__input_data_i[0xeU])),16);
    bufp->chgSData(oldp+163,((vlSelfRef.fc_layer__DOT__input_data_i[0xeU] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+164,((0xffffU & vlSelfRef.fc_layer__DOT__input_data_i[0xfU])),16);
    bufp->chgSData(oldp+165,((vlSelfRef.fc_layer__DOT__input_data_i[0xfU] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+166,((0xffffU & vlSelfRef.fc_layer__DOT__input_data_i[0x10U])),16);
    bufp->chgSData(oldp+167,((vlSelfRef.fc_layer__DOT__input_data_i[0x10U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+168,((0xffffU & vlSelfRef.fc_layer__DOT__input_data_i[0x11U])),16);
    bufp->chgSData(oldp+169,((vlSelfRef.fc_layer__DOT__input_data_i[0x11U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+170,((0xffffU & vlSelfRef.fc_layer__DOT__input_data_i[0x12U])),16);
    bufp->chgSData(oldp+171,((vlSelfRef.fc_layer__DOT__input_data_i[0x12U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+172,((0xffffU & vlSelfRef.fc_layer__DOT__input_data_i[0x13U])),16);
    bufp->chgSData(oldp+173,((vlSelfRef.fc_layer__DOT__input_data_i[0x13U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+174,((0xffffU & vlSelfRef.fc_layer__DOT__input_data_i[0x14U])),16);
    bufp->chgSData(oldp+175,((vlSelfRef.fc_layer__DOT__input_data_i[0x14U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+176,((0xffffU & vlSelfRef.fc_layer__DOT__input_data_i[0x15U])),16);
    bufp->chgSData(oldp+177,((vlSelfRef.fc_layer__DOT__input_data_i[0x15U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+178,((0xffffU & vlSelfRef.fc_layer__DOT__input_data_i[0x16U])),16);
    bufp->chgSData(oldp+179,((vlSelfRef.fc_layer__DOT__input_data_i[0x16U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+180,((0xffffU & vlSelfRef.fc_layer__DOT__input_data_i[0x17U])),16);
    bufp->chgSData(oldp+181,((vlSelfRef.fc_layer__DOT__input_data_i[0x17U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+182,((0xffffU & vlSelfRef.fc_layer__DOT__input_data_i[0x18U])),16);
    bufp->chgSData(oldp+183,((vlSelfRef.fc_layer__DOT__input_data_i[0x18U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+184,((0xffffU & vlSelfRef.fc_layer__DOT__input_data_i[0x19U])),16);
    bufp->chgSData(oldp+185,((vlSelfRef.fc_layer__DOT__input_data_i[0x19U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+186,((0xffffU & vlSelfRef.fc_layer__DOT__input_data_i[0x1aU])),16);
    bufp->chgSData(oldp+187,((vlSelfRef.fc_layer__DOT__input_data_i[0x1aU] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+188,((0xffffU & vlSelfRef.fc_layer__DOT__input_data_i[0x1bU])),16);
    bufp->chgSData(oldp+189,((vlSelfRef.fc_layer__DOT__input_data_i[0x1bU] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+190,((0xffffU & vlSelfRef.fc_layer__DOT__input_data_i[0x1cU])),16);
    bufp->chgSData(oldp+191,((vlSelfRef.fc_layer__DOT__input_data_i[0x1cU] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+192,((0xffffU & vlSelfRef.fc_layer__DOT__input_data_i[0x1dU])),16);
    bufp->chgSData(oldp+193,((vlSelfRef.fc_layer__DOT__input_data_i[0x1dU] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+194,((0xffffU & vlSelfRef.fc_layer__DOT__input_data_i[0x1eU])),16);
    bufp->chgSData(oldp+195,((vlSelfRef.fc_layer__DOT__input_data_i[0x1eU] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+196,((0xffffU & vlSelfRef.fc_layer__DOT__input_data_i[0x1fU])),16);
    bufp->chgSData(oldp+197,((vlSelfRef.fc_layer__DOT__input_data_i[0x1fU] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+198,((0xffffU & vlSelfRef.fc_layer__DOT__input_data_i[0x20U])),16);
    bufp->chgSData(oldp+199,((vlSelfRef.fc_layer__DOT__input_data_i[0x20U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+200,((0xffffU & vlSelfRef.fc_layer__DOT__input_data_i[0x21U])),16);
    bufp->chgSData(oldp+201,((vlSelfRef.fc_layer__DOT__input_data_i[0x21U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+202,((0xffffU & vlSelfRef.fc_layer__DOT__input_data_i[0x22U])),16);
    bufp->chgSData(oldp+203,((vlSelfRef.fc_layer__DOT__input_data_i[0x22U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+204,((0xffffU & vlSelfRef.fc_layer__DOT__input_data_i[0x23U])),16);
    bufp->chgSData(oldp+205,((vlSelfRef.fc_layer__DOT__input_data_i[0x23U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+206,((0xffffU & vlSelfRef.fc_layer__DOT__input_data_i[0x24U])),16);
    bufp->chgSData(oldp+207,((vlSelfRef.fc_layer__DOT__input_data_i[0x24U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+208,((0xffffU & vlSelfRef.fc_layer__DOT__input_data_i[0x25U])),16);
    bufp->chgSData(oldp+209,((vlSelfRef.fc_layer__DOT__input_data_i[0x25U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+210,((0xffffU & vlSelfRef.fc_layer__DOT__input_data_i[0x26U])),16);
    bufp->chgSData(oldp+211,((vlSelfRef.fc_layer__DOT__input_data_i[0x26U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+212,((0xffffU & vlSelfRef.fc_layer__DOT__input_data_i[0x27U])),16);
    bufp->chgSData(oldp+213,((vlSelfRef.fc_layer__DOT__input_data_i[0x27U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+214,((0xffffU & vlSelfRef.fc_layer__DOT__input_data_i[0x28U])),16);
    bufp->chgSData(oldp+215,((vlSelfRef.fc_layer__DOT__input_data_i[0x28U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+216,((0xffffU & vlSelfRef.fc_layer__DOT__input_data_i[0x29U])),16);
    bufp->chgSData(oldp+217,((vlSelfRef.fc_layer__DOT__input_data_i[0x29U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+218,((0xffffU & vlSelfRef.fc_layer__DOT__input_data_i[0x2aU])),16);
    bufp->chgSData(oldp+219,((vlSelfRef.fc_layer__DOT__input_data_i[0x2aU] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+220,((0xffffU & vlSelfRef.fc_layer__DOT__input_data_i[0x2bU])),16);
    bufp->chgSData(oldp+221,((vlSelfRef.fc_layer__DOT__input_data_i[0x2bU] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+222,((0xffffU & vlSelfRef.fc_layer__DOT__input_data_i[0x2cU])),16);
    bufp->chgSData(oldp+223,((vlSelfRef.fc_layer__DOT__input_data_i[0x2cU] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+224,((0xffffU & vlSelfRef.fc_layer__DOT__input_data_i[0x2dU])),16);
    bufp->chgSData(oldp+225,((vlSelfRef.fc_layer__DOT__input_data_i[0x2dU] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+226,((0xffffU & vlSelfRef.fc_layer__DOT__input_data_i[0x2eU])),16);
    bufp->chgSData(oldp+227,((vlSelfRef.fc_layer__DOT__input_data_i[0x2eU] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+228,((0xffffU & vlSelfRef.fc_layer__DOT__input_data_i[0x2fU])),16);
    bufp->chgSData(oldp+229,((vlSelfRef.fc_layer__DOT__input_data_i[0x2fU] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+230,((0xffffU & vlSelfRef.fc_layer__DOT__input_data_i[0x30U])),16);
    bufp->chgSData(oldp+231,((vlSelfRef.fc_layer__DOT__input_data_i[0x30U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+232,((0xffffU & vlSelfRef.fc_layer__DOT__input_data_i[0x31U])),16);
    bufp->chgSData(oldp+233,((vlSelfRef.fc_layer__DOT__input_data_i[0x31U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+234,(vlSelfRef.fc_layer__DOT__bias_addr_i),10);
    bufp->chgSData(oldp+235,(vlSelfRef.fc_layer__DOT__bias_data_i),16);
    bufp->chgBit(oldp+236,(vlSelfRef.fc_layer__DOT__bias_we_i));
    bufp->chgSData(oldp+237,((0xffffU & vlSelfRef.fc_layer__DOT__output_data_o[0U])),16);
    bufp->chgSData(oldp+238,((vlSelfRef.fc_layer__DOT__output_data_o[0U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+239,((0xffffU & vlSelfRef.fc_layer__DOT__output_data_o[1U])),16);
    bufp->chgSData(oldp+240,((vlSelfRef.fc_layer__DOT__output_data_o[1U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+241,((0xffffU & vlSelfRef.fc_layer__DOT__output_data_o[2U])),16);
    bufp->chgSData(oldp+242,((vlSelfRef.fc_layer__DOT__output_data_o[2U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+243,((0xffffU & vlSelfRef.fc_layer__DOT__output_data_o[3U])),16);
    bufp->chgSData(oldp+244,((vlSelfRef.fc_layer__DOT__output_data_o[3U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+245,((0xffffU & vlSelfRef.fc_layer__DOT__output_data_o[4U])),16);
    bufp->chgSData(oldp+246,((vlSelfRef.fc_layer__DOT__output_data_o[4U] 
                              >> 0x10U)),16);
    bufp->chgBit(oldp+247,(vlSelfRef.fc_layer__DOT__valid_o));
    bufp->chgIData(oldp+248,(vlSelfRef.fc_layer__DOT__debug_state_o),32);
    bufp->chgSData(oldp+249,(vlSelfRef.fc_layer__DOT__debug_accumulator_o),16);
    bufp->chgSData(oldp+250,(vlSelfRef.fc_layer__DOT__debug_addr_counter_o),10);
    bufp->chgCData(oldp+251,(vlSelfRef.fc_layer__DOT__debug_flags_o),4);
    bufp->chgSData(oldp+252,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0U])),16);
    bufp->chgSData(oldp+253,((vlSelfRef.fc_layer__DOT__weight_memory[0U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+254,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[1U])),16);
    bufp->chgSData(oldp+255,((vlSelfRef.fc_layer__DOT__weight_memory[1U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+256,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[2U])),16);
    bufp->chgSData(oldp+257,((vlSelfRef.fc_layer__DOT__weight_memory[2U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+258,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[3U])),16);
    bufp->chgSData(oldp+259,((vlSelfRef.fc_layer__DOT__weight_memory[3U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+260,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[4U])),16);
    bufp->chgSData(oldp+261,((vlSelfRef.fc_layer__DOT__weight_memory[4U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+262,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[5U])),16);
    bufp->chgSData(oldp+263,((vlSelfRef.fc_layer__DOT__weight_memory[5U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+264,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[6U])),16);
    bufp->chgSData(oldp+265,((vlSelfRef.fc_layer__DOT__weight_memory[6U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+266,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[7U])),16);
    bufp->chgSData(oldp+267,((vlSelfRef.fc_layer__DOT__weight_memory[7U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+268,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[8U])),16);
    bufp->chgSData(oldp+269,((vlSelfRef.fc_layer__DOT__weight_memory[8U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+270,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[9U])),16);
    bufp->chgSData(oldp+271,((vlSelfRef.fc_layer__DOT__weight_memory[9U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+272,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0xaU])),16);
    bufp->chgSData(oldp+273,((vlSelfRef.fc_layer__DOT__weight_memory[0xaU] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+274,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0xbU])),16);
    bufp->chgSData(oldp+275,((vlSelfRef.fc_layer__DOT__weight_memory[0xbU] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+276,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0xcU])),16);
    bufp->chgSData(oldp+277,((vlSelfRef.fc_layer__DOT__weight_memory[0xcU] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+278,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0xdU])),16);
    bufp->chgSData(oldp+279,((vlSelfRef.fc_layer__DOT__weight_memory[0xdU] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+280,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0xeU])),16);
    bufp->chgSData(oldp+281,((vlSelfRef.fc_layer__DOT__weight_memory[0xeU] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+282,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0xfU])),16);
    bufp->chgSData(oldp+283,((vlSelfRef.fc_layer__DOT__weight_memory[0xfU] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+284,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x10U])),16);
    bufp->chgSData(oldp+285,((vlSelfRef.fc_layer__DOT__weight_memory[0x10U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+286,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x11U])),16);
    bufp->chgSData(oldp+287,((vlSelfRef.fc_layer__DOT__weight_memory[0x11U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+288,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x12U])),16);
    bufp->chgSData(oldp+289,((vlSelfRef.fc_layer__DOT__weight_memory[0x12U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+290,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x13U])),16);
    bufp->chgSData(oldp+291,((vlSelfRef.fc_layer__DOT__weight_memory[0x13U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+292,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x14U])),16);
    bufp->chgSData(oldp+293,((vlSelfRef.fc_layer__DOT__weight_memory[0x14U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+294,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x15U])),16);
    bufp->chgSData(oldp+295,((vlSelfRef.fc_layer__DOT__weight_memory[0x15U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+296,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x16U])),16);
    bufp->chgSData(oldp+297,((vlSelfRef.fc_layer__DOT__weight_memory[0x16U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+298,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x17U])),16);
    bufp->chgSData(oldp+299,((vlSelfRef.fc_layer__DOT__weight_memory[0x17U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+300,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x18U])),16);
    bufp->chgSData(oldp+301,((vlSelfRef.fc_layer__DOT__weight_memory[0x18U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+302,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x19U])),16);
    bufp->chgSData(oldp+303,((vlSelfRef.fc_layer__DOT__weight_memory[0x19U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+304,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x1aU])),16);
    bufp->chgSData(oldp+305,((vlSelfRef.fc_layer__DOT__weight_memory[0x1aU] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+306,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x1bU])),16);
    bufp->chgSData(oldp+307,((vlSelfRef.fc_layer__DOT__weight_memory[0x1bU] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+308,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x1cU])),16);
    bufp->chgSData(oldp+309,((vlSelfRef.fc_layer__DOT__weight_memory[0x1cU] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+310,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x1dU])),16);
    bufp->chgSData(oldp+311,((vlSelfRef.fc_layer__DOT__weight_memory[0x1dU] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+312,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x1eU])),16);
    bufp->chgSData(oldp+313,((vlSelfRef.fc_layer__DOT__weight_memory[0x1eU] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+314,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x1fU])),16);
    bufp->chgSData(oldp+315,((vlSelfRef.fc_layer__DOT__weight_memory[0x1fU] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+316,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x20U])),16);
    bufp->chgSData(oldp+317,((vlSelfRef.fc_layer__DOT__weight_memory[0x20U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+318,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x21U])),16);
    bufp->chgSData(oldp+319,((vlSelfRef.fc_layer__DOT__weight_memory[0x21U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+320,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x22U])),16);
    bufp->chgSData(oldp+321,((vlSelfRef.fc_layer__DOT__weight_memory[0x22U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+322,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x23U])),16);
    bufp->chgSData(oldp+323,((vlSelfRef.fc_layer__DOT__weight_memory[0x23U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+324,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x24U])),16);
    bufp->chgSData(oldp+325,((vlSelfRef.fc_layer__DOT__weight_memory[0x24U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+326,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x25U])),16);
    bufp->chgSData(oldp+327,((vlSelfRef.fc_layer__DOT__weight_memory[0x25U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+328,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x26U])),16);
    bufp->chgSData(oldp+329,((vlSelfRef.fc_layer__DOT__weight_memory[0x26U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+330,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x27U])),16);
    bufp->chgSData(oldp+331,((vlSelfRef.fc_layer__DOT__weight_memory[0x27U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+332,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x28U])),16);
    bufp->chgSData(oldp+333,((vlSelfRef.fc_layer__DOT__weight_memory[0x28U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+334,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x29U])),16);
    bufp->chgSData(oldp+335,((vlSelfRef.fc_layer__DOT__weight_memory[0x29U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+336,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x2aU])),16);
    bufp->chgSData(oldp+337,((vlSelfRef.fc_layer__DOT__weight_memory[0x2aU] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+338,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x2bU])),16);
    bufp->chgSData(oldp+339,((vlSelfRef.fc_layer__DOT__weight_memory[0x2bU] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+340,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x2cU])),16);
    bufp->chgSData(oldp+341,((vlSelfRef.fc_layer__DOT__weight_memory[0x2cU] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+342,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x2dU])),16);
    bufp->chgSData(oldp+343,((vlSelfRef.fc_layer__DOT__weight_memory[0x2dU] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+344,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x2eU])),16);
    bufp->chgSData(oldp+345,((vlSelfRef.fc_layer__DOT__weight_memory[0x2eU] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+346,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x2fU])),16);
    bufp->chgSData(oldp+347,((vlSelfRef.fc_layer__DOT__weight_memory[0x2fU] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+348,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x30U])),16);
    bufp->chgSData(oldp+349,((vlSelfRef.fc_layer__DOT__weight_memory[0x30U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+350,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x31U])),16);
    bufp->chgSData(oldp+351,((vlSelfRef.fc_layer__DOT__weight_memory[0x31U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+352,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x32U])),16);
    bufp->chgSData(oldp+353,((vlSelfRef.fc_layer__DOT__weight_memory[0x32U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+354,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x33U])),16);
    bufp->chgSData(oldp+355,((vlSelfRef.fc_layer__DOT__weight_memory[0x33U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+356,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x34U])),16);
    bufp->chgSData(oldp+357,((vlSelfRef.fc_layer__DOT__weight_memory[0x34U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+358,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x35U])),16);
    bufp->chgSData(oldp+359,((vlSelfRef.fc_layer__DOT__weight_memory[0x35U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+360,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x36U])),16);
    bufp->chgSData(oldp+361,((vlSelfRef.fc_layer__DOT__weight_memory[0x36U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+362,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x37U])),16);
    bufp->chgSData(oldp+363,((vlSelfRef.fc_layer__DOT__weight_memory[0x37U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+364,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x38U])),16);
    bufp->chgSData(oldp+365,((vlSelfRef.fc_layer__DOT__weight_memory[0x38U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+366,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x39U])),16);
    bufp->chgSData(oldp+367,((vlSelfRef.fc_layer__DOT__weight_memory[0x39U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+368,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x3aU])),16);
    bufp->chgSData(oldp+369,((vlSelfRef.fc_layer__DOT__weight_memory[0x3aU] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+370,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x3bU])),16);
    bufp->chgSData(oldp+371,((vlSelfRef.fc_layer__DOT__weight_memory[0x3bU] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+372,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x3cU])),16);
    bufp->chgSData(oldp+373,((vlSelfRef.fc_layer__DOT__weight_memory[0x3cU] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+374,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x3dU])),16);
    bufp->chgSData(oldp+375,((vlSelfRef.fc_layer__DOT__weight_memory[0x3dU] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+376,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x3eU])),16);
    bufp->chgSData(oldp+377,((vlSelfRef.fc_layer__DOT__weight_memory[0x3eU] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+378,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x3fU])),16);
    bufp->chgSData(oldp+379,((vlSelfRef.fc_layer__DOT__weight_memory[0x3fU] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+380,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x40U])),16);
    bufp->chgSData(oldp+381,((vlSelfRef.fc_layer__DOT__weight_memory[0x40U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+382,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x41U])),16);
    bufp->chgSData(oldp+383,((vlSelfRef.fc_layer__DOT__weight_memory[0x41U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+384,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x42U])),16);
    bufp->chgSData(oldp+385,((vlSelfRef.fc_layer__DOT__weight_memory[0x42U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+386,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x43U])),16);
    bufp->chgSData(oldp+387,((vlSelfRef.fc_layer__DOT__weight_memory[0x43U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+388,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x44U])),16);
    bufp->chgSData(oldp+389,((vlSelfRef.fc_layer__DOT__weight_memory[0x44U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+390,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x45U])),16);
    bufp->chgSData(oldp+391,((vlSelfRef.fc_layer__DOT__weight_memory[0x45U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+392,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x46U])),16);
    bufp->chgSData(oldp+393,((vlSelfRef.fc_layer__DOT__weight_memory[0x46U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+394,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x47U])),16);
    bufp->chgSData(oldp+395,((vlSelfRef.fc_layer__DOT__weight_memory[0x47U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+396,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x48U])),16);
    bufp->chgSData(oldp+397,((vlSelfRef.fc_layer__DOT__weight_memory[0x48U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+398,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x49U])),16);
    bufp->chgSData(oldp+399,((vlSelfRef.fc_layer__DOT__weight_memory[0x49U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+400,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x4aU])),16);
    bufp->chgSData(oldp+401,((vlSelfRef.fc_layer__DOT__weight_memory[0x4aU] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+402,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x4bU])),16);
    bufp->chgSData(oldp+403,((vlSelfRef.fc_layer__DOT__weight_memory[0x4bU] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+404,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x4cU])),16);
    bufp->chgSData(oldp+405,((vlSelfRef.fc_layer__DOT__weight_memory[0x4cU] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+406,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x4dU])),16);
    bufp->chgSData(oldp+407,((vlSelfRef.fc_layer__DOT__weight_memory[0x4dU] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+408,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x4eU])),16);
    bufp->chgSData(oldp+409,((vlSelfRef.fc_layer__DOT__weight_memory[0x4eU] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+410,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x4fU])),16);
    bufp->chgSData(oldp+411,((vlSelfRef.fc_layer__DOT__weight_memory[0x4fU] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+412,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x50U])),16);
    bufp->chgSData(oldp+413,((vlSelfRef.fc_layer__DOT__weight_memory[0x50U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+414,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x51U])),16);
    bufp->chgSData(oldp+415,((vlSelfRef.fc_layer__DOT__weight_memory[0x51U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+416,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x52U])),16);
    bufp->chgSData(oldp+417,((vlSelfRef.fc_layer__DOT__weight_memory[0x52U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+418,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x53U])),16);
    bufp->chgSData(oldp+419,((vlSelfRef.fc_layer__DOT__weight_memory[0x53U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+420,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x54U])),16);
    bufp->chgSData(oldp+421,((vlSelfRef.fc_layer__DOT__weight_memory[0x54U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+422,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x55U])),16);
    bufp->chgSData(oldp+423,((vlSelfRef.fc_layer__DOT__weight_memory[0x55U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+424,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x56U])),16);
    bufp->chgSData(oldp+425,((vlSelfRef.fc_layer__DOT__weight_memory[0x56U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+426,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x57U])),16);
    bufp->chgSData(oldp+427,((vlSelfRef.fc_layer__DOT__weight_memory[0x57U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+428,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x58U])),16);
    bufp->chgSData(oldp+429,((vlSelfRef.fc_layer__DOT__weight_memory[0x58U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+430,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x59U])),16);
    bufp->chgSData(oldp+431,((vlSelfRef.fc_layer__DOT__weight_memory[0x59U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+432,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x5aU])),16);
    bufp->chgSData(oldp+433,((vlSelfRef.fc_layer__DOT__weight_memory[0x5aU] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+434,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x5bU])),16);
    bufp->chgSData(oldp+435,((vlSelfRef.fc_layer__DOT__weight_memory[0x5bU] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+436,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x5cU])),16);
    bufp->chgSData(oldp+437,((vlSelfRef.fc_layer__DOT__weight_memory[0x5cU] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+438,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x5dU])),16);
    bufp->chgSData(oldp+439,((vlSelfRef.fc_layer__DOT__weight_memory[0x5dU] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+440,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x5eU])),16);
    bufp->chgSData(oldp+441,((vlSelfRef.fc_layer__DOT__weight_memory[0x5eU] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+442,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x5fU])),16);
    bufp->chgSData(oldp+443,((vlSelfRef.fc_layer__DOT__weight_memory[0x5fU] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+444,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x60U])),16);
    bufp->chgSData(oldp+445,((vlSelfRef.fc_layer__DOT__weight_memory[0x60U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+446,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x61U])),16);
    bufp->chgSData(oldp+447,((vlSelfRef.fc_layer__DOT__weight_memory[0x61U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+448,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x62U])),16);
    bufp->chgSData(oldp+449,((vlSelfRef.fc_layer__DOT__weight_memory[0x62U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+450,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x63U])),16);
    bufp->chgSData(oldp+451,((vlSelfRef.fc_layer__DOT__weight_memory[0x63U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+452,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x64U])),16);
    bufp->chgSData(oldp+453,((vlSelfRef.fc_layer__DOT__weight_memory[0x64U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+454,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x65U])),16);
    bufp->chgSData(oldp+455,((vlSelfRef.fc_layer__DOT__weight_memory[0x65U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+456,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x66U])),16);
    bufp->chgSData(oldp+457,((vlSelfRef.fc_layer__DOT__weight_memory[0x66U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+458,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x67U])),16);
    bufp->chgSData(oldp+459,((vlSelfRef.fc_layer__DOT__weight_memory[0x67U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+460,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x68U])),16);
    bufp->chgSData(oldp+461,((vlSelfRef.fc_layer__DOT__weight_memory[0x68U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+462,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x69U])),16);
    bufp->chgSData(oldp+463,((vlSelfRef.fc_layer__DOT__weight_memory[0x69U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+464,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x6aU])),16);
    bufp->chgSData(oldp+465,((vlSelfRef.fc_layer__DOT__weight_memory[0x6aU] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+466,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x6bU])),16);
    bufp->chgSData(oldp+467,((vlSelfRef.fc_layer__DOT__weight_memory[0x6bU] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+468,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x6cU])),16);
    bufp->chgSData(oldp+469,((vlSelfRef.fc_layer__DOT__weight_memory[0x6cU] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+470,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x6dU])),16);
    bufp->chgSData(oldp+471,((vlSelfRef.fc_layer__DOT__weight_memory[0x6dU] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+472,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x6eU])),16);
    bufp->chgSData(oldp+473,((vlSelfRef.fc_layer__DOT__weight_memory[0x6eU] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+474,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x6fU])),16);
    bufp->chgSData(oldp+475,((vlSelfRef.fc_layer__DOT__weight_memory[0x6fU] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+476,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x70U])),16);
    bufp->chgSData(oldp+477,((vlSelfRef.fc_layer__DOT__weight_memory[0x70U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+478,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x71U])),16);
    bufp->chgSData(oldp+479,((vlSelfRef.fc_layer__DOT__weight_memory[0x71U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+480,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x72U])),16);
    bufp->chgSData(oldp+481,((vlSelfRef.fc_layer__DOT__weight_memory[0x72U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+482,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x73U])),16);
    bufp->chgSData(oldp+483,((vlSelfRef.fc_layer__DOT__weight_memory[0x73U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+484,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x74U])),16);
    bufp->chgSData(oldp+485,((vlSelfRef.fc_layer__DOT__weight_memory[0x74U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+486,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x75U])),16);
    bufp->chgSData(oldp+487,((vlSelfRef.fc_layer__DOT__weight_memory[0x75U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+488,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x76U])),16);
    bufp->chgSData(oldp+489,((vlSelfRef.fc_layer__DOT__weight_memory[0x76U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+490,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x77U])),16);
    bufp->chgSData(oldp+491,((vlSelfRef.fc_layer__DOT__weight_memory[0x77U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+492,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x78U])),16);
    bufp->chgSData(oldp+493,((vlSelfRef.fc_layer__DOT__weight_memory[0x78U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+494,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x79U])),16);
    bufp->chgSData(oldp+495,((vlSelfRef.fc_layer__DOT__weight_memory[0x79U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+496,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x7aU])),16);
    bufp->chgSData(oldp+497,((vlSelfRef.fc_layer__DOT__weight_memory[0x7aU] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+498,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x7bU])),16);
    bufp->chgSData(oldp+499,((vlSelfRef.fc_layer__DOT__weight_memory[0x7bU] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+500,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x7cU])),16);
    bufp->chgSData(oldp+501,((vlSelfRef.fc_layer__DOT__weight_memory[0x7cU] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+502,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x7dU])),16);
    bufp->chgSData(oldp+503,((vlSelfRef.fc_layer__DOT__weight_memory[0x7dU] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+504,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x7eU])),16);
    bufp->chgSData(oldp+505,((vlSelfRef.fc_layer__DOT__weight_memory[0x7eU] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+506,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x7fU])),16);
    bufp->chgSData(oldp+507,((vlSelfRef.fc_layer__DOT__weight_memory[0x7fU] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+508,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x80U])),16);
    bufp->chgSData(oldp+509,((vlSelfRef.fc_layer__DOT__weight_memory[0x80U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+510,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x81U])),16);
    bufp->chgSData(oldp+511,((vlSelfRef.fc_layer__DOT__weight_memory[0x81U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+512,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x82U])),16);
    bufp->chgSData(oldp+513,((vlSelfRef.fc_layer__DOT__weight_memory[0x82U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+514,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x83U])),16);
    bufp->chgSData(oldp+515,((vlSelfRef.fc_layer__DOT__weight_memory[0x83U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+516,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x84U])),16);
    bufp->chgSData(oldp+517,((vlSelfRef.fc_layer__DOT__weight_memory[0x84U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+518,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x85U])),16);
    bufp->chgSData(oldp+519,((vlSelfRef.fc_layer__DOT__weight_memory[0x85U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+520,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x86U])),16);
    bufp->chgSData(oldp+521,((vlSelfRef.fc_layer__DOT__weight_memory[0x86U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+522,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x87U])),16);
    bufp->chgSData(oldp+523,((vlSelfRef.fc_layer__DOT__weight_memory[0x87U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+524,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x88U])),16);
    bufp->chgSData(oldp+525,((vlSelfRef.fc_layer__DOT__weight_memory[0x88U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+526,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x89U])),16);
    bufp->chgSData(oldp+527,((vlSelfRef.fc_layer__DOT__weight_memory[0x89U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+528,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x8aU])),16);
    bufp->chgSData(oldp+529,((vlSelfRef.fc_layer__DOT__weight_memory[0x8aU] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+530,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x8bU])),16);
    bufp->chgSData(oldp+531,((vlSelfRef.fc_layer__DOT__weight_memory[0x8bU] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+532,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x8cU])),16);
    bufp->chgSData(oldp+533,((vlSelfRef.fc_layer__DOT__weight_memory[0x8cU] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+534,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x8dU])),16);
    bufp->chgSData(oldp+535,((vlSelfRef.fc_layer__DOT__weight_memory[0x8dU] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+536,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x8eU])),16);
    bufp->chgSData(oldp+537,((vlSelfRef.fc_layer__DOT__weight_memory[0x8eU] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+538,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x8fU])),16);
    bufp->chgSData(oldp+539,((vlSelfRef.fc_layer__DOT__weight_memory[0x8fU] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+540,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x90U])),16);
    bufp->chgSData(oldp+541,((vlSelfRef.fc_layer__DOT__weight_memory[0x90U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+542,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x91U])),16);
    bufp->chgSData(oldp+543,((vlSelfRef.fc_layer__DOT__weight_memory[0x91U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+544,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x92U])),16);
    bufp->chgSData(oldp+545,((vlSelfRef.fc_layer__DOT__weight_memory[0x92U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+546,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x93U])),16);
    bufp->chgSData(oldp+547,((vlSelfRef.fc_layer__DOT__weight_memory[0x93U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+548,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x94U])),16);
    bufp->chgSData(oldp+549,((vlSelfRef.fc_layer__DOT__weight_memory[0x94U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+550,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x95U])),16);
    bufp->chgSData(oldp+551,((vlSelfRef.fc_layer__DOT__weight_memory[0x95U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+552,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x96U])),16);
    bufp->chgSData(oldp+553,((vlSelfRef.fc_layer__DOT__weight_memory[0x96U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+554,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x97U])),16);
    bufp->chgSData(oldp+555,((vlSelfRef.fc_layer__DOT__weight_memory[0x97U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+556,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x98U])),16);
    bufp->chgSData(oldp+557,((vlSelfRef.fc_layer__DOT__weight_memory[0x98U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+558,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x99U])),16);
    bufp->chgSData(oldp+559,((vlSelfRef.fc_layer__DOT__weight_memory[0x99U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+560,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x9aU])),16);
    bufp->chgSData(oldp+561,((vlSelfRef.fc_layer__DOT__weight_memory[0x9aU] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+562,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x9bU])),16);
    bufp->chgSData(oldp+563,((vlSelfRef.fc_layer__DOT__weight_memory[0x9bU] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+564,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x9cU])),16);
    bufp->chgSData(oldp+565,((vlSelfRef.fc_layer__DOT__weight_memory[0x9cU] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+566,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x9dU])),16);
    bufp->chgSData(oldp+567,((vlSelfRef.fc_layer__DOT__weight_memory[0x9dU] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+568,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x9eU])),16);
    bufp->chgSData(oldp+569,((vlSelfRef.fc_layer__DOT__weight_memory[0x9eU] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+570,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x9fU])),16);
    bufp->chgSData(oldp+571,((vlSelfRef.fc_layer__DOT__weight_memory[0x9fU] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+572,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0xa0U])),16);
    bufp->chgSData(oldp+573,((vlSelfRef.fc_layer__DOT__weight_memory[0xa0U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+574,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0xa1U])),16);
    bufp->chgSData(oldp+575,((vlSelfRef.fc_layer__DOT__weight_memory[0xa1U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+576,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0xa2U])),16);
    bufp->chgSData(oldp+577,((vlSelfRef.fc_layer__DOT__weight_memory[0xa2U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+578,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0xa3U])),16);
    bufp->chgSData(oldp+579,((vlSelfRef.fc_layer__DOT__weight_memory[0xa3U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+580,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0xa4U])),16);
    bufp->chgSData(oldp+581,((vlSelfRef.fc_layer__DOT__weight_memory[0xa4U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+582,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0xa5U])),16);
    bufp->chgSData(oldp+583,((vlSelfRef.fc_layer__DOT__weight_memory[0xa5U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+584,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0xa6U])),16);
    bufp->chgSData(oldp+585,((vlSelfRef.fc_layer__DOT__weight_memory[0xa6U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+586,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0xa7U])),16);
    bufp->chgSData(oldp+587,((vlSelfRef.fc_layer__DOT__weight_memory[0xa7U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+588,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0xa8U])),16);
    bufp->chgSData(oldp+589,((vlSelfRef.fc_layer__DOT__weight_memory[0xa8U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+590,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0xa9U])),16);
    bufp->chgSData(oldp+591,((vlSelfRef.fc_layer__DOT__weight_memory[0xa9U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+592,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0xaaU])),16);
    bufp->chgSData(oldp+593,((vlSelfRef.fc_layer__DOT__weight_memory[0xaaU] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+594,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0xabU])),16);
    bufp->chgSData(oldp+595,((vlSelfRef.fc_layer__DOT__weight_memory[0xabU] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+596,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0xacU])),16);
    bufp->chgSData(oldp+597,((vlSelfRef.fc_layer__DOT__weight_memory[0xacU] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+598,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0xadU])),16);
    bufp->chgSData(oldp+599,((vlSelfRef.fc_layer__DOT__weight_memory[0xadU] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+600,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0xaeU])),16);
    bufp->chgSData(oldp+601,((vlSelfRef.fc_layer__DOT__weight_memory[0xaeU] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+602,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0xafU])),16);
    bufp->chgSData(oldp+603,((vlSelfRef.fc_layer__DOT__weight_memory[0xafU] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+604,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0xb0U])),16);
    bufp->chgSData(oldp+605,((vlSelfRef.fc_layer__DOT__weight_memory[0xb0U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+606,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0xb1U])),16);
    bufp->chgSData(oldp+607,((vlSelfRef.fc_layer__DOT__weight_memory[0xb1U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+608,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0xb2U])),16);
    bufp->chgSData(oldp+609,((vlSelfRef.fc_layer__DOT__weight_memory[0xb2U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+610,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0xb3U])),16);
    bufp->chgSData(oldp+611,((vlSelfRef.fc_layer__DOT__weight_memory[0xb3U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+612,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0xb4U])),16);
    bufp->chgSData(oldp+613,((vlSelfRef.fc_layer__DOT__weight_memory[0xb4U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+614,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0xb5U])),16);
    bufp->chgSData(oldp+615,((vlSelfRef.fc_layer__DOT__weight_memory[0xb5U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+616,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0xb6U])),16);
    bufp->chgSData(oldp+617,((vlSelfRef.fc_layer__DOT__weight_memory[0xb6U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+618,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0xb7U])),16);
    bufp->chgSData(oldp+619,((vlSelfRef.fc_layer__DOT__weight_memory[0xb7U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+620,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0xb8U])),16);
    bufp->chgSData(oldp+621,((vlSelfRef.fc_layer__DOT__weight_memory[0xb8U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+622,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0xb9U])),16);
    bufp->chgSData(oldp+623,((vlSelfRef.fc_layer__DOT__weight_memory[0xb9U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+624,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0xbaU])),16);
    bufp->chgSData(oldp+625,((vlSelfRef.fc_layer__DOT__weight_memory[0xbaU] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+626,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0xbbU])),16);
    bufp->chgSData(oldp+627,((vlSelfRef.fc_layer__DOT__weight_memory[0xbbU] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+628,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0xbcU])),16);
    bufp->chgSData(oldp+629,((vlSelfRef.fc_layer__DOT__weight_memory[0xbcU] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+630,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0xbdU])),16);
    bufp->chgSData(oldp+631,((vlSelfRef.fc_layer__DOT__weight_memory[0xbdU] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+632,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0xbeU])),16);
    bufp->chgSData(oldp+633,((vlSelfRef.fc_layer__DOT__weight_memory[0xbeU] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+634,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0xbfU])),16);
    bufp->chgSData(oldp+635,((vlSelfRef.fc_layer__DOT__weight_memory[0xbfU] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+636,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0xc0U])),16);
    bufp->chgSData(oldp+637,((vlSelfRef.fc_layer__DOT__weight_memory[0xc0U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+638,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0xc1U])),16);
    bufp->chgSData(oldp+639,((vlSelfRef.fc_layer__DOT__weight_memory[0xc1U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+640,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0xc2U])),16);
    bufp->chgSData(oldp+641,((vlSelfRef.fc_layer__DOT__weight_memory[0xc2U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+642,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0xc3U])),16);
    bufp->chgSData(oldp+643,((vlSelfRef.fc_layer__DOT__weight_memory[0xc3U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+644,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0xc4U])),16);
    bufp->chgSData(oldp+645,((vlSelfRef.fc_layer__DOT__weight_memory[0xc4U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+646,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0xc5U])),16);
    bufp->chgSData(oldp+647,((vlSelfRef.fc_layer__DOT__weight_memory[0xc5U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+648,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0xc6U])),16);
    bufp->chgSData(oldp+649,((vlSelfRef.fc_layer__DOT__weight_memory[0xc6U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+650,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0xc7U])),16);
    bufp->chgSData(oldp+651,((vlSelfRef.fc_layer__DOT__weight_memory[0xc7U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+652,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0xc8U])),16);
    bufp->chgSData(oldp+653,((vlSelfRef.fc_layer__DOT__weight_memory[0xc8U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+654,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0xc9U])),16);
    bufp->chgSData(oldp+655,((vlSelfRef.fc_layer__DOT__weight_memory[0xc9U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+656,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0xcaU])),16);
    bufp->chgSData(oldp+657,((vlSelfRef.fc_layer__DOT__weight_memory[0xcaU] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+658,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0xcbU])),16);
    bufp->chgSData(oldp+659,((vlSelfRef.fc_layer__DOT__weight_memory[0xcbU] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+660,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0xccU])),16);
    bufp->chgSData(oldp+661,((vlSelfRef.fc_layer__DOT__weight_memory[0xccU] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+662,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0xcdU])),16);
    bufp->chgSData(oldp+663,((vlSelfRef.fc_layer__DOT__weight_memory[0xcdU] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+664,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0xceU])),16);
    bufp->chgSData(oldp+665,((vlSelfRef.fc_layer__DOT__weight_memory[0xceU] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+666,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0xcfU])),16);
    bufp->chgSData(oldp+667,((vlSelfRef.fc_layer__DOT__weight_memory[0xcfU] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+668,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0xd0U])),16);
    bufp->chgSData(oldp+669,((vlSelfRef.fc_layer__DOT__weight_memory[0xd0U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+670,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0xd1U])),16);
    bufp->chgSData(oldp+671,((vlSelfRef.fc_layer__DOT__weight_memory[0xd1U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+672,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0xd2U])),16);
    bufp->chgSData(oldp+673,((vlSelfRef.fc_layer__DOT__weight_memory[0xd2U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+674,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0xd3U])),16);
    bufp->chgSData(oldp+675,((vlSelfRef.fc_layer__DOT__weight_memory[0xd3U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+676,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0xd4U])),16);
    bufp->chgSData(oldp+677,((vlSelfRef.fc_layer__DOT__weight_memory[0xd4U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+678,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0xd5U])),16);
    bufp->chgSData(oldp+679,((vlSelfRef.fc_layer__DOT__weight_memory[0xd5U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+680,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0xd6U])),16);
    bufp->chgSData(oldp+681,((vlSelfRef.fc_layer__DOT__weight_memory[0xd6U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+682,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0xd7U])),16);
    bufp->chgSData(oldp+683,((vlSelfRef.fc_layer__DOT__weight_memory[0xd7U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+684,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0xd8U])),16);
    bufp->chgSData(oldp+685,((vlSelfRef.fc_layer__DOT__weight_memory[0xd8U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+686,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0xd9U])),16);
    bufp->chgSData(oldp+687,((vlSelfRef.fc_layer__DOT__weight_memory[0xd9U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+688,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0xdaU])),16);
    bufp->chgSData(oldp+689,((vlSelfRef.fc_layer__DOT__weight_memory[0xdaU] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+690,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0xdbU])),16);
    bufp->chgSData(oldp+691,((vlSelfRef.fc_layer__DOT__weight_memory[0xdbU] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+692,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0xdcU])),16);
    bufp->chgSData(oldp+693,((vlSelfRef.fc_layer__DOT__weight_memory[0xdcU] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+694,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0xddU])),16);
    bufp->chgSData(oldp+695,((vlSelfRef.fc_layer__DOT__weight_memory[0xddU] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+696,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0xdeU])),16);
    bufp->chgSData(oldp+697,((vlSelfRef.fc_layer__DOT__weight_memory[0xdeU] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+698,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0xdfU])),16);
    bufp->chgSData(oldp+699,((vlSelfRef.fc_layer__DOT__weight_memory[0xdfU] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+700,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0xe0U])),16);
    bufp->chgSData(oldp+701,((vlSelfRef.fc_layer__DOT__weight_memory[0xe0U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+702,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0xe1U])),16);
    bufp->chgSData(oldp+703,((vlSelfRef.fc_layer__DOT__weight_memory[0xe1U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+704,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0xe2U])),16);
    bufp->chgSData(oldp+705,((vlSelfRef.fc_layer__DOT__weight_memory[0xe2U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+706,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0xe3U])),16);
    bufp->chgSData(oldp+707,((vlSelfRef.fc_layer__DOT__weight_memory[0xe3U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+708,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0xe4U])),16);
    bufp->chgSData(oldp+709,((vlSelfRef.fc_layer__DOT__weight_memory[0xe4U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+710,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0xe5U])),16);
    bufp->chgSData(oldp+711,((vlSelfRef.fc_layer__DOT__weight_memory[0xe5U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+712,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0xe6U])),16);
    bufp->chgSData(oldp+713,((vlSelfRef.fc_layer__DOT__weight_memory[0xe6U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+714,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0xe7U])),16);
    bufp->chgSData(oldp+715,((vlSelfRef.fc_layer__DOT__weight_memory[0xe7U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+716,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0xe8U])),16);
    bufp->chgSData(oldp+717,((vlSelfRef.fc_layer__DOT__weight_memory[0xe8U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+718,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0xe9U])),16);
    bufp->chgSData(oldp+719,((vlSelfRef.fc_layer__DOT__weight_memory[0xe9U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+720,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0xeaU])),16);
    bufp->chgSData(oldp+721,((vlSelfRef.fc_layer__DOT__weight_memory[0xeaU] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+722,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0xebU])),16);
    bufp->chgSData(oldp+723,((vlSelfRef.fc_layer__DOT__weight_memory[0xebU] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+724,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0xecU])),16);
    bufp->chgSData(oldp+725,((vlSelfRef.fc_layer__DOT__weight_memory[0xecU] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+726,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0xedU])),16);
    bufp->chgSData(oldp+727,((vlSelfRef.fc_layer__DOT__weight_memory[0xedU] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+728,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0xeeU])),16);
    bufp->chgSData(oldp+729,((vlSelfRef.fc_layer__DOT__weight_memory[0xeeU] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+730,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0xefU])),16);
    bufp->chgSData(oldp+731,((vlSelfRef.fc_layer__DOT__weight_memory[0xefU] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+732,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0xf0U])),16);
    bufp->chgSData(oldp+733,((vlSelfRef.fc_layer__DOT__weight_memory[0xf0U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+734,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0xf1U])),16);
    bufp->chgSData(oldp+735,((vlSelfRef.fc_layer__DOT__weight_memory[0xf1U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+736,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0xf2U])),16);
    bufp->chgSData(oldp+737,((vlSelfRef.fc_layer__DOT__weight_memory[0xf2U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+738,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0xf3U])),16);
    bufp->chgSData(oldp+739,((vlSelfRef.fc_layer__DOT__weight_memory[0xf3U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+740,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0xf4U])),16);
    bufp->chgSData(oldp+741,((vlSelfRef.fc_layer__DOT__weight_memory[0xf4U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+742,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0xf5U])),16);
    bufp->chgSData(oldp+743,((vlSelfRef.fc_layer__DOT__weight_memory[0xf5U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+744,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0xf6U])),16);
    bufp->chgSData(oldp+745,((vlSelfRef.fc_layer__DOT__weight_memory[0xf6U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+746,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0xf7U])),16);
    bufp->chgSData(oldp+747,((vlSelfRef.fc_layer__DOT__weight_memory[0xf7U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+748,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0xf8U])),16);
    bufp->chgSData(oldp+749,((vlSelfRef.fc_layer__DOT__weight_memory[0xf8U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+750,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0xf9U])),16);
    bufp->chgSData(oldp+751,((vlSelfRef.fc_layer__DOT__weight_memory[0xf9U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+752,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0xfaU])),16);
    bufp->chgSData(oldp+753,((vlSelfRef.fc_layer__DOT__weight_memory[0xfaU] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+754,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0xfbU])),16);
    bufp->chgSData(oldp+755,((vlSelfRef.fc_layer__DOT__weight_memory[0xfbU] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+756,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0xfcU])),16);
    bufp->chgSData(oldp+757,((vlSelfRef.fc_layer__DOT__weight_memory[0xfcU] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+758,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0xfdU])),16);
    bufp->chgSData(oldp+759,((vlSelfRef.fc_layer__DOT__weight_memory[0xfdU] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+760,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0xfeU])),16);
    bufp->chgSData(oldp+761,((vlSelfRef.fc_layer__DOT__weight_memory[0xfeU] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+762,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0xffU])),16);
    bufp->chgSData(oldp+763,((vlSelfRef.fc_layer__DOT__weight_memory[0xffU] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+764,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x100U])),16);
    bufp->chgSData(oldp+765,((vlSelfRef.fc_layer__DOT__weight_memory[0x100U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+766,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x101U])),16);
    bufp->chgSData(oldp+767,((vlSelfRef.fc_layer__DOT__weight_memory[0x101U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+768,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x102U])),16);
    bufp->chgSData(oldp+769,((vlSelfRef.fc_layer__DOT__weight_memory[0x102U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+770,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x103U])),16);
    bufp->chgSData(oldp+771,((vlSelfRef.fc_layer__DOT__weight_memory[0x103U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+772,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x104U])),16);
    bufp->chgSData(oldp+773,((vlSelfRef.fc_layer__DOT__weight_memory[0x104U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+774,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x105U])),16);
    bufp->chgSData(oldp+775,((vlSelfRef.fc_layer__DOT__weight_memory[0x105U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+776,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x106U])),16);
    bufp->chgSData(oldp+777,((vlSelfRef.fc_layer__DOT__weight_memory[0x106U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+778,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x107U])),16);
    bufp->chgSData(oldp+779,((vlSelfRef.fc_layer__DOT__weight_memory[0x107U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+780,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x108U])),16);
    bufp->chgSData(oldp+781,((vlSelfRef.fc_layer__DOT__weight_memory[0x108U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+782,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x109U])),16);
    bufp->chgSData(oldp+783,((vlSelfRef.fc_layer__DOT__weight_memory[0x109U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+784,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x10aU])),16);
    bufp->chgSData(oldp+785,((vlSelfRef.fc_layer__DOT__weight_memory[0x10aU] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+786,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x10bU])),16);
    bufp->chgSData(oldp+787,((vlSelfRef.fc_layer__DOT__weight_memory[0x10bU] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+788,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x10cU])),16);
    bufp->chgSData(oldp+789,((vlSelfRef.fc_layer__DOT__weight_memory[0x10cU] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+790,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x10dU])),16);
    bufp->chgSData(oldp+791,((vlSelfRef.fc_layer__DOT__weight_memory[0x10dU] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+792,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x10eU])),16);
    bufp->chgSData(oldp+793,((vlSelfRef.fc_layer__DOT__weight_memory[0x10eU] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+794,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x10fU])),16);
    bufp->chgSData(oldp+795,((vlSelfRef.fc_layer__DOT__weight_memory[0x10fU] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+796,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x110U])),16);
    bufp->chgSData(oldp+797,((vlSelfRef.fc_layer__DOT__weight_memory[0x110U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+798,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x111U])),16);
    bufp->chgSData(oldp+799,((vlSelfRef.fc_layer__DOT__weight_memory[0x111U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+800,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x112U])),16);
    bufp->chgSData(oldp+801,((vlSelfRef.fc_layer__DOT__weight_memory[0x112U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+802,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x113U])),16);
    bufp->chgSData(oldp+803,((vlSelfRef.fc_layer__DOT__weight_memory[0x113U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+804,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x114U])),16);
    bufp->chgSData(oldp+805,((vlSelfRef.fc_layer__DOT__weight_memory[0x114U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+806,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x115U])),16);
    bufp->chgSData(oldp+807,((vlSelfRef.fc_layer__DOT__weight_memory[0x115U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+808,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x116U])),16);
    bufp->chgSData(oldp+809,((vlSelfRef.fc_layer__DOT__weight_memory[0x116U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+810,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x117U])),16);
    bufp->chgSData(oldp+811,((vlSelfRef.fc_layer__DOT__weight_memory[0x117U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+812,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x118U])),16);
    bufp->chgSData(oldp+813,((vlSelfRef.fc_layer__DOT__weight_memory[0x118U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+814,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x119U])),16);
    bufp->chgSData(oldp+815,((vlSelfRef.fc_layer__DOT__weight_memory[0x119U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+816,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x11aU])),16);
    bufp->chgSData(oldp+817,((vlSelfRef.fc_layer__DOT__weight_memory[0x11aU] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+818,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x11bU])),16);
    bufp->chgSData(oldp+819,((vlSelfRef.fc_layer__DOT__weight_memory[0x11bU] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+820,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x11cU])),16);
    bufp->chgSData(oldp+821,((vlSelfRef.fc_layer__DOT__weight_memory[0x11cU] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+822,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x11dU])),16);
    bufp->chgSData(oldp+823,((vlSelfRef.fc_layer__DOT__weight_memory[0x11dU] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+824,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x11eU])),16);
    bufp->chgSData(oldp+825,((vlSelfRef.fc_layer__DOT__weight_memory[0x11eU] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+826,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x11fU])),16);
    bufp->chgSData(oldp+827,((vlSelfRef.fc_layer__DOT__weight_memory[0x11fU] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+828,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x120U])),16);
    bufp->chgSData(oldp+829,((vlSelfRef.fc_layer__DOT__weight_memory[0x120U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+830,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x121U])),16);
    bufp->chgSData(oldp+831,((vlSelfRef.fc_layer__DOT__weight_memory[0x121U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+832,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x122U])),16);
    bufp->chgSData(oldp+833,((vlSelfRef.fc_layer__DOT__weight_memory[0x122U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+834,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x123U])),16);
    bufp->chgSData(oldp+835,((vlSelfRef.fc_layer__DOT__weight_memory[0x123U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+836,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x124U])),16);
    bufp->chgSData(oldp+837,((vlSelfRef.fc_layer__DOT__weight_memory[0x124U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+838,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x125U])),16);
    bufp->chgSData(oldp+839,((vlSelfRef.fc_layer__DOT__weight_memory[0x125U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+840,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x126U])),16);
    bufp->chgSData(oldp+841,((vlSelfRef.fc_layer__DOT__weight_memory[0x126U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+842,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x127U])),16);
    bufp->chgSData(oldp+843,((vlSelfRef.fc_layer__DOT__weight_memory[0x127U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+844,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x128U])),16);
    bufp->chgSData(oldp+845,((vlSelfRef.fc_layer__DOT__weight_memory[0x128U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+846,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x129U])),16);
    bufp->chgSData(oldp+847,((vlSelfRef.fc_layer__DOT__weight_memory[0x129U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+848,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x12aU])),16);
    bufp->chgSData(oldp+849,((vlSelfRef.fc_layer__DOT__weight_memory[0x12aU] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+850,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x12bU])),16);
    bufp->chgSData(oldp+851,((vlSelfRef.fc_layer__DOT__weight_memory[0x12bU] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+852,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x12cU])),16);
    bufp->chgSData(oldp+853,((vlSelfRef.fc_layer__DOT__weight_memory[0x12cU] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+854,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x12dU])),16);
    bufp->chgSData(oldp+855,((vlSelfRef.fc_layer__DOT__weight_memory[0x12dU] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+856,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x12eU])),16);
    bufp->chgSData(oldp+857,((vlSelfRef.fc_layer__DOT__weight_memory[0x12eU] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+858,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x12fU])),16);
    bufp->chgSData(oldp+859,((vlSelfRef.fc_layer__DOT__weight_memory[0x12fU] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+860,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x130U])),16);
    bufp->chgSData(oldp+861,((vlSelfRef.fc_layer__DOT__weight_memory[0x130U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+862,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x131U])),16);
    bufp->chgSData(oldp+863,((vlSelfRef.fc_layer__DOT__weight_memory[0x131U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+864,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x132U])),16);
    bufp->chgSData(oldp+865,((vlSelfRef.fc_layer__DOT__weight_memory[0x132U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+866,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x133U])),16);
    bufp->chgSData(oldp+867,((vlSelfRef.fc_layer__DOT__weight_memory[0x133U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+868,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x134U])),16);
    bufp->chgSData(oldp+869,((vlSelfRef.fc_layer__DOT__weight_memory[0x134U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+870,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x135U])),16);
    bufp->chgSData(oldp+871,((vlSelfRef.fc_layer__DOT__weight_memory[0x135U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+872,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x136U])),16);
    bufp->chgSData(oldp+873,((vlSelfRef.fc_layer__DOT__weight_memory[0x136U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+874,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x137U])),16);
    bufp->chgSData(oldp+875,((vlSelfRef.fc_layer__DOT__weight_memory[0x137U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+876,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x138U])),16);
    bufp->chgSData(oldp+877,((vlSelfRef.fc_layer__DOT__weight_memory[0x138U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+878,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x139U])),16);
    bufp->chgSData(oldp+879,((vlSelfRef.fc_layer__DOT__weight_memory[0x139U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+880,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x13aU])),16);
    bufp->chgSData(oldp+881,((vlSelfRef.fc_layer__DOT__weight_memory[0x13aU] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+882,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x13bU])),16);
    bufp->chgSData(oldp+883,((vlSelfRef.fc_layer__DOT__weight_memory[0x13bU] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+884,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x13cU])),16);
    bufp->chgSData(oldp+885,((vlSelfRef.fc_layer__DOT__weight_memory[0x13cU] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+886,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x13dU])),16);
    bufp->chgSData(oldp+887,((vlSelfRef.fc_layer__DOT__weight_memory[0x13dU] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+888,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x13eU])),16);
    bufp->chgSData(oldp+889,((vlSelfRef.fc_layer__DOT__weight_memory[0x13eU] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+890,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x13fU])),16);
    bufp->chgSData(oldp+891,((vlSelfRef.fc_layer__DOT__weight_memory[0x13fU] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+892,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x140U])),16);
    bufp->chgSData(oldp+893,((vlSelfRef.fc_layer__DOT__weight_memory[0x140U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+894,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x141U])),16);
    bufp->chgSData(oldp+895,((vlSelfRef.fc_layer__DOT__weight_memory[0x141U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+896,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x142U])),16);
    bufp->chgSData(oldp+897,((vlSelfRef.fc_layer__DOT__weight_memory[0x142U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+898,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x143U])),16);
    bufp->chgSData(oldp+899,((vlSelfRef.fc_layer__DOT__weight_memory[0x143U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+900,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x144U])),16);
    bufp->chgSData(oldp+901,((vlSelfRef.fc_layer__DOT__weight_memory[0x144U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+902,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x145U])),16);
    bufp->chgSData(oldp+903,((vlSelfRef.fc_layer__DOT__weight_memory[0x145U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+904,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x146U])),16);
    bufp->chgSData(oldp+905,((vlSelfRef.fc_layer__DOT__weight_memory[0x146U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+906,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x147U])),16);
    bufp->chgSData(oldp+907,((vlSelfRef.fc_layer__DOT__weight_memory[0x147U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+908,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x148U])),16);
    bufp->chgSData(oldp+909,((vlSelfRef.fc_layer__DOT__weight_memory[0x148U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+910,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x149U])),16);
    bufp->chgSData(oldp+911,((vlSelfRef.fc_layer__DOT__weight_memory[0x149U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+912,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x14aU])),16);
    bufp->chgSData(oldp+913,((vlSelfRef.fc_layer__DOT__weight_memory[0x14aU] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+914,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x14bU])),16);
    bufp->chgSData(oldp+915,((vlSelfRef.fc_layer__DOT__weight_memory[0x14bU] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+916,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x14cU])),16);
    bufp->chgSData(oldp+917,((vlSelfRef.fc_layer__DOT__weight_memory[0x14cU] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+918,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x14dU])),16);
    bufp->chgSData(oldp+919,((vlSelfRef.fc_layer__DOT__weight_memory[0x14dU] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+920,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x14eU])),16);
    bufp->chgSData(oldp+921,((vlSelfRef.fc_layer__DOT__weight_memory[0x14eU] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+922,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x14fU])),16);
    bufp->chgSData(oldp+923,((vlSelfRef.fc_layer__DOT__weight_memory[0x14fU] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+924,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x150U])),16);
    bufp->chgSData(oldp+925,((vlSelfRef.fc_layer__DOT__weight_memory[0x150U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+926,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x151U])),16);
    bufp->chgSData(oldp+927,((vlSelfRef.fc_layer__DOT__weight_memory[0x151U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+928,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x152U])),16);
    bufp->chgSData(oldp+929,((vlSelfRef.fc_layer__DOT__weight_memory[0x152U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+930,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x153U])),16);
    bufp->chgSData(oldp+931,((vlSelfRef.fc_layer__DOT__weight_memory[0x153U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+932,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x154U])),16);
    bufp->chgSData(oldp+933,((vlSelfRef.fc_layer__DOT__weight_memory[0x154U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+934,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x155U])),16);
    bufp->chgSData(oldp+935,((vlSelfRef.fc_layer__DOT__weight_memory[0x155U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+936,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x156U])),16);
    bufp->chgSData(oldp+937,((vlSelfRef.fc_layer__DOT__weight_memory[0x156U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+938,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x157U])),16);
    bufp->chgSData(oldp+939,((vlSelfRef.fc_layer__DOT__weight_memory[0x157U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+940,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x158U])),16);
    bufp->chgSData(oldp+941,((vlSelfRef.fc_layer__DOT__weight_memory[0x158U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+942,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x159U])),16);
    bufp->chgSData(oldp+943,((vlSelfRef.fc_layer__DOT__weight_memory[0x159U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+944,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x15aU])),16);
    bufp->chgSData(oldp+945,((vlSelfRef.fc_layer__DOT__weight_memory[0x15aU] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+946,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x15bU])),16);
    bufp->chgSData(oldp+947,((vlSelfRef.fc_layer__DOT__weight_memory[0x15bU] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+948,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x15cU])),16);
    bufp->chgSData(oldp+949,((vlSelfRef.fc_layer__DOT__weight_memory[0x15cU] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+950,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x15dU])),16);
    bufp->chgSData(oldp+951,((vlSelfRef.fc_layer__DOT__weight_memory[0x15dU] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+952,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x15eU])),16);
    bufp->chgSData(oldp+953,((vlSelfRef.fc_layer__DOT__weight_memory[0x15eU] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+954,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x15fU])),16);
    bufp->chgSData(oldp+955,((vlSelfRef.fc_layer__DOT__weight_memory[0x15fU] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+956,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x160U])),16);
    bufp->chgSData(oldp+957,((vlSelfRef.fc_layer__DOT__weight_memory[0x160U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+958,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x161U])),16);
    bufp->chgSData(oldp+959,((vlSelfRef.fc_layer__DOT__weight_memory[0x161U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+960,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x162U])),16);
    bufp->chgSData(oldp+961,((vlSelfRef.fc_layer__DOT__weight_memory[0x162U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+962,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x163U])),16);
    bufp->chgSData(oldp+963,((vlSelfRef.fc_layer__DOT__weight_memory[0x163U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+964,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x164U])),16);
    bufp->chgSData(oldp+965,((vlSelfRef.fc_layer__DOT__weight_memory[0x164U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+966,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x165U])),16);
    bufp->chgSData(oldp+967,((vlSelfRef.fc_layer__DOT__weight_memory[0x165U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+968,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x166U])),16);
    bufp->chgSData(oldp+969,((vlSelfRef.fc_layer__DOT__weight_memory[0x166U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+970,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x167U])),16);
    bufp->chgSData(oldp+971,((vlSelfRef.fc_layer__DOT__weight_memory[0x167U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+972,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x168U])),16);
    bufp->chgSData(oldp+973,((vlSelfRef.fc_layer__DOT__weight_memory[0x168U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+974,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x169U])),16);
    bufp->chgSData(oldp+975,((vlSelfRef.fc_layer__DOT__weight_memory[0x169U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+976,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x16aU])),16);
    bufp->chgSData(oldp+977,((vlSelfRef.fc_layer__DOT__weight_memory[0x16aU] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+978,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x16bU])),16);
    bufp->chgSData(oldp+979,((vlSelfRef.fc_layer__DOT__weight_memory[0x16bU] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+980,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x16cU])),16);
    bufp->chgSData(oldp+981,((vlSelfRef.fc_layer__DOT__weight_memory[0x16cU] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+982,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x16dU])),16);
    bufp->chgSData(oldp+983,((vlSelfRef.fc_layer__DOT__weight_memory[0x16dU] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+984,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x16eU])),16);
    bufp->chgSData(oldp+985,((vlSelfRef.fc_layer__DOT__weight_memory[0x16eU] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+986,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x16fU])),16);
    bufp->chgSData(oldp+987,((vlSelfRef.fc_layer__DOT__weight_memory[0x16fU] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+988,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x170U])),16);
    bufp->chgSData(oldp+989,((vlSelfRef.fc_layer__DOT__weight_memory[0x170U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+990,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x171U])),16);
    bufp->chgSData(oldp+991,((vlSelfRef.fc_layer__DOT__weight_memory[0x171U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+992,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x172U])),16);
    bufp->chgSData(oldp+993,((vlSelfRef.fc_layer__DOT__weight_memory[0x172U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+994,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x173U])),16);
    bufp->chgSData(oldp+995,((vlSelfRef.fc_layer__DOT__weight_memory[0x173U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+996,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x174U])),16);
    bufp->chgSData(oldp+997,((vlSelfRef.fc_layer__DOT__weight_memory[0x174U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+998,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x175U])),16);
    bufp->chgSData(oldp+999,((vlSelfRef.fc_layer__DOT__weight_memory[0x175U] 
                              >> 0x10U)),16);
    bufp->chgSData(oldp+1000,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x176U])),16);
    bufp->chgSData(oldp+1001,((vlSelfRef.fc_layer__DOT__weight_memory[0x176U] 
                               >> 0x10U)),16);
    bufp->chgSData(oldp+1002,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x177U])),16);
    bufp->chgSData(oldp+1003,((vlSelfRef.fc_layer__DOT__weight_memory[0x177U] 
                               >> 0x10U)),16);
    bufp->chgSData(oldp+1004,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x178U])),16);
    bufp->chgSData(oldp+1005,((vlSelfRef.fc_layer__DOT__weight_memory[0x178U] 
                               >> 0x10U)),16);
    bufp->chgSData(oldp+1006,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x179U])),16);
    bufp->chgSData(oldp+1007,((vlSelfRef.fc_layer__DOT__weight_memory[0x179U] 
                               >> 0x10U)),16);
    bufp->chgSData(oldp+1008,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x17aU])),16);
    bufp->chgSData(oldp+1009,((vlSelfRef.fc_layer__DOT__weight_memory[0x17aU] 
                               >> 0x10U)),16);
    bufp->chgSData(oldp+1010,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x17bU])),16);
    bufp->chgSData(oldp+1011,((vlSelfRef.fc_layer__DOT__weight_memory[0x17bU] 
                               >> 0x10U)),16);
    bufp->chgSData(oldp+1012,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x17cU])),16);
    bufp->chgSData(oldp+1013,((vlSelfRef.fc_layer__DOT__weight_memory[0x17cU] 
                               >> 0x10U)),16);
    bufp->chgSData(oldp+1014,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x17dU])),16);
    bufp->chgSData(oldp+1015,((vlSelfRef.fc_layer__DOT__weight_memory[0x17dU] 
                               >> 0x10U)),16);
    bufp->chgSData(oldp+1016,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x17eU])),16);
    bufp->chgSData(oldp+1017,((vlSelfRef.fc_layer__DOT__weight_memory[0x17eU] 
                               >> 0x10U)),16);
    bufp->chgSData(oldp+1018,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x17fU])),16);
    bufp->chgSData(oldp+1019,((vlSelfRef.fc_layer__DOT__weight_memory[0x17fU] 
                               >> 0x10U)),16);
    bufp->chgSData(oldp+1020,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x180U])),16);
    bufp->chgSData(oldp+1021,((vlSelfRef.fc_layer__DOT__weight_memory[0x180U] 
                               >> 0x10U)),16);
    bufp->chgSData(oldp+1022,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x181U])),16);
    bufp->chgSData(oldp+1023,((vlSelfRef.fc_layer__DOT__weight_memory[0x181U] 
                               >> 0x10U)),16);
    bufp->chgSData(oldp+1024,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x182U])),16);
    bufp->chgSData(oldp+1025,((vlSelfRef.fc_layer__DOT__weight_memory[0x182U] 
                               >> 0x10U)),16);
    bufp->chgSData(oldp+1026,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x183U])),16);
    bufp->chgSData(oldp+1027,((vlSelfRef.fc_layer__DOT__weight_memory[0x183U] 
                               >> 0x10U)),16);
    bufp->chgSData(oldp+1028,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x184U])),16);
    bufp->chgSData(oldp+1029,((vlSelfRef.fc_layer__DOT__weight_memory[0x184U] 
                               >> 0x10U)),16);
    bufp->chgSData(oldp+1030,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x185U])),16);
    bufp->chgSData(oldp+1031,((vlSelfRef.fc_layer__DOT__weight_memory[0x185U] 
                               >> 0x10U)),16);
    bufp->chgSData(oldp+1032,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x186U])),16);
    bufp->chgSData(oldp+1033,((vlSelfRef.fc_layer__DOT__weight_memory[0x186U] 
                               >> 0x10U)),16);
    bufp->chgSData(oldp+1034,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x187U])),16);
    bufp->chgSData(oldp+1035,((vlSelfRef.fc_layer__DOT__weight_memory[0x187U] 
                               >> 0x10U)),16);
    bufp->chgSData(oldp+1036,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x188U])),16);
    bufp->chgSData(oldp+1037,((vlSelfRef.fc_layer__DOT__weight_memory[0x188U] 
                               >> 0x10U)),16);
    bufp->chgSData(oldp+1038,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x189U])),16);
    bufp->chgSData(oldp+1039,((vlSelfRef.fc_layer__DOT__weight_memory[0x189U] 
                               >> 0x10U)),16);
    bufp->chgSData(oldp+1040,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x18aU])),16);
    bufp->chgSData(oldp+1041,((vlSelfRef.fc_layer__DOT__weight_memory[0x18aU] 
                               >> 0x10U)),16);
    bufp->chgSData(oldp+1042,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x18bU])),16);
    bufp->chgSData(oldp+1043,((vlSelfRef.fc_layer__DOT__weight_memory[0x18bU] 
                               >> 0x10U)),16);
    bufp->chgSData(oldp+1044,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x18cU])),16);
    bufp->chgSData(oldp+1045,((vlSelfRef.fc_layer__DOT__weight_memory[0x18cU] 
                               >> 0x10U)),16);
    bufp->chgSData(oldp+1046,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x18dU])),16);
    bufp->chgSData(oldp+1047,((vlSelfRef.fc_layer__DOT__weight_memory[0x18dU] 
                               >> 0x10U)),16);
    bufp->chgSData(oldp+1048,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x18eU])),16);
    bufp->chgSData(oldp+1049,((vlSelfRef.fc_layer__DOT__weight_memory[0x18eU] 
                               >> 0x10U)),16);
    bufp->chgSData(oldp+1050,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x18fU])),16);
    bufp->chgSData(oldp+1051,((vlSelfRef.fc_layer__DOT__weight_memory[0x18fU] 
                               >> 0x10U)),16);
    bufp->chgSData(oldp+1052,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x190U])),16);
    bufp->chgSData(oldp+1053,((vlSelfRef.fc_layer__DOT__weight_memory[0x190U] 
                               >> 0x10U)),16);
    bufp->chgSData(oldp+1054,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x191U])),16);
    bufp->chgSData(oldp+1055,((vlSelfRef.fc_layer__DOT__weight_memory[0x191U] 
                               >> 0x10U)),16);
    bufp->chgSData(oldp+1056,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x192U])),16);
    bufp->chgSData(oldp+1057,((vlSelfRef.fc_layer__DOT__weight_memory[0x192U] 
                               >> 0x10U)),16);
    bufp->chgSData(oldp+1058,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x193U])),16);
    bufp->chgSData(oldp+1059,((vlSelfRef.fc_layer__DOT__weight_memory[0x193U] 
                               >> 0x10U)),16);
    bufp->chgSData(oldp+1060,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x194U])),16);
    bufp->chgSData(oldp+1061,((vlSelfRef.fc_layer__DOT__weight_memory[0x194U] 
                               >> 0x10U)),16);
    bufp->chgSData(oldp+1062,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x195U])),16);
    bufp->chgSData(oldp+1063,((vlSelfRef.fc_layer__DOT__weight_memory[0x195U] 
                               >> 0x10U)),16);
    bufp->chgSData(oldp+1064,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x196U])),16);
    bufp->chgSData(oldp+1065,((vlSelfRef.fc_layer__DOT__weight_memory[0x196U] 
                               >> 0x10U)),16);
    bufp->chgSData(oldp+1066,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x197U])),16);
    bufp->chgSData(oldp+1067,((vlSelfRef.fc_layer__DOT__weight_memory[0x197U] 
                               >> 0x10U)),16);
    bufp->chgSData(oldp+1068,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x198U])),16);
    bufp->chgSData(oldp+1069,((vlSelfRef.fc_layer__DOT__weight_memory[0x198U] 
                               >> 0x10U)),16);
    bufp->chgSData(oldp+1070,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x199U])),16);
    bufp->chgSData(oldp+1071,((vlSelfRef.fc_layer__DOT__weight_memory[0x199U] 
                               >> 0x10U)),16);
    bufp->chgSData(oldp+1072,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x19aU])),16);
    bufp->chgSData(oldp+1073,((vlSelfRef.fc_layer__DOT__weight_memory[0x19aU] 
                               >> 0x10U)),16);
    bufp->chgSData(oldp+1074,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x19bU])),16);
    bufp->chgSData(oldp+1075,((vlSelfRef.fc_layer__DOT__weight_memory[0x19bU] 
                               >> 0x10U)),16);
    bufp->chgSData(oldp+1076,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x19cU])),16);
    bufp->chgSData(oldp+1077,((vlSelfRef.fc_layer__DOT__weight_memory[0x19cU] 
                               >> 0x10U)),16);
    bufp->chgSData(oldp+1078,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x19dU])),16);
    bufp->chgSData(oldp+1079,((vlSelfRef.fc_layer__DOT__weight_memory[0x19dU] 
                               >> 0x10U)),16);
    bufp->chgSData(oldp+1080,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x19eU])),16);
    bufp->chgSData(oldp+1081,((vlSelfRef.fc_layer__DOT__weight_memory[0x19eU] 
                               >> 0x10U)),16);
    bufp->chgSData(oldp+1082,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x19fU])),16);
    bufp->chgSData(oldp+1083,((vlSelfRef.fc_layer__DOT__weight_memory[0x19fU] 
                               >> 0x10U)),16);
    bufp->chgSData(oldp+1084,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x1a0U])),16);
    bufp->chgSData(oldp+1085,((vlSelfRef.fc_layer__DOT__weight_memory[0x1a0U] 
                               >> 0x10U)),16);
    bufp->chgSData(oldp+1086,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x1a1U])),16);
    bufp->chgSData(oldp+1087,((vlSelfRef.fc_layer__DOT__weight_memory[0x1a1U] 
                               >> 0x10U)),16);
    bufp->chgSData(oldp+1088,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x1a2U])),16);
    bufp->chgSData(oldp+1089,((vlSelfRef.fc_layer__DOT__weight_memory[0x1a2U] 
                               >> 0x10U)),16);
    bufp->chgSData(oldp+1090,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x1a3U])),16);
    bufp->chgSData(oldp+1091,((vlSelfRef.fc_layer__DOT__weight_memory[0x1a3U] 
                               >> 0x10U)),16);
    bufp->chgSData(oldp+1092,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x1a4U])),16);
    bufp->chgSData(oldp+1093,((vlSelfRef.fc_layer__DOT__weight_memory[0x1a4U] 
                               >> 0x10U)),16);
    bufp->chgSData(oldp+1094,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x1a5U])),16);
    bufp->chgSData(oldp+1095,((vlSelfRef.fc_layer__DOT__weight_memory[0x1a5U] 
                               >> 0x10U)),16);
    bufp->chgSData(oldp+1096,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x1a6U])),16);
    bufp->chgSData(oldp+1097,((vlSelfRef.fc_layer__DOT__weight_memory[0x1a6U] 
                               >> 0x10U)),16);
    bufp->chgSData(oldp+1098,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x1a7U])),16);
    bufp->chgSData(oldp+1099,((vlSelfRef.fc_layer__DOT__weight_memory[0x1a7U] 
                               >> 0x10U)),16);
    bufp->chgSData(oldp+1100,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x1a8U])),16);
    bufp->chgSData(oldp+1101,((vlSelfRef.fc_layer__DOT__weight_memory[0x1a8U] 
                               >> 0x10U)),16);
    bufp->chgSData(oldp+1102,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x1a9U])),16);
    bufp->chgSData(oldp+1103,((vlSelfRef.fc_layer__DOT__weight_memory[0x1a9U] 
                               >> 0x10U)),16);
    bufp->chgSData(oldp+1104,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x1aaU])),16);
    bufp->chgSData(oldp+1105,((vlSelfRef.fc_layer__DOT__weight_memory[0x1aaU] 
                               >> 0x10U)),16);
    bufp->chgSData(oldp+1106,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x1abU])),16);
    bufp->chgSData(oldp+1107,((vlSelfRef.fc_layer__DOT__weight_memory[0x1abU] 
                               >> 0x10U)),16);
    bufp->chgSData(oldp+1108,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x1acU])),16);
    bufp->chgSData(oldp+1109,((vlSelfRef.fc_layer__DOT__weight_memory[0x1acU] 
                               >> 0x10U)),16);
    bufp->chgSData(oldp+1110,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x1adU])),16);
    bufp->chgSData(oldp+1111,((vlSelfRef.fc_layer__DOT__weight_memory[0x1adU] 
                               >> 0x10U)),16);
    bufp->chgSData(oldp+1112,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x1aeU])),16);
    bufp->chgSData(oldp+1113,((vlSelfRef.fc_layer__DOT__weight_memory[0x1aeU] 
                               >> 0x10U)),16);
    bufp->chgSData(oldp+1114,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x1afU])),16);
    bufp->chgSData(oldp+1115,((vlSelfRef.fc_layer__DOT__weight_memory[0x1afU] 
                               >> 0x10U)),16);
    bufp->chgSData(oldp+1116,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x1b0U])),16);
    bufp->chgSData(oldp+1117,((vlSelfRef.fc_layer__DOT__weight_memory[0x1b0U] 
                               >> 0x10U)),16);
    bufp->chgSData(oldp+1118,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x1b1U])),16);
    bufp->chgSData(oldp+1119,((vlSelfRef.fc_layer__DOT__weight_memory[0x1b1U] 
                               >> 0x10U)),16);
    bufp->chgSData(oldp+1120,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x1b2U])),16);
    bufp->chgSData(oldp+1121,((vlSelfRef.fc_layer__DOT__weight_memory[0x1b2U] 
                               >> 0x10U)),16);
    bufp->chgSData(oldp+1122,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x1b3U])),16);
    bufp->chgSData(oldp+1123,((vlSelfRef.fc_layer__DOT__weight_memory[0x1b3U] 
                               >> 0x10U)),16);
    bufp->chgSData(oldp+1124,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x1b4U])),16);
    bufp->chgSData(oldp+1125,((vlSelfRef.fc_layer__DOT__weight_memory[0x1b4U] 
                               >> 0x10U)),16);
    bufp->chgSData(oldp+1126,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x1b5U])),16);
    bufp->chgSData(oldp+1127,((vlSelfRef.fc_layer__DOT__weight_memory[0x1b5U] 
                               >> 0x10U)),16);
    bufp->chgSData(oldp+1128,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x1b6U])),16);
    bufp->chgSData(oldp+1129,((vlSelfRef.fc_layer__DOT__weight_memory[0x1b6U] 
                               >> 0x10U)),16);
    bufp->chgSData(oldp+1130,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x1b7U])),16);
    bufp->chgSData(oldp+1131,((vlSelfRef.fc_layer__DOT__weight_memory[0x1b7U] 
                               >> 0x10U)),16);
    bufp->chgSData(oldp+1132,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x1b8U])),16);
    bufp->chgSData(oldp+1133,((vlSelfRef.fc_layer__DOT__weight_memory[0x1b8U] 
                               >> 0x10U)),16);
    bufp->chgSData(oldp+1134,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x1b9U])),16);
    bufp->chgSData(oldp+1135,((vlSelfRef.fc_layer__DOT__weight_memory[0x1b9U] 
                               >> 0x10U)),16);
    bufp->chgSData(oldp+1136,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x1baU])),16);
    bufp->chgSData(oldp+1137,((vlSelfRef.fc_layer__DOT__weight_memory[0x1baU] 
                               >> 0x10U)),16);
    bufp->chgSData(oldp+1138,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x1bbU])),16);
    bufp->chgSData(oldp+1139,((vlSelfRef.fc_layer__DOT__weight_memory[0x1bbU] 
                               >> 0x10U)),16);
    bufp->chgSData(oldp+1140,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x1bcU])),16);
    bufp->chgSData(oldp+1141,((vlSelfRef.fc_layer__DOT__weight_memory[0x1bcU] 
                               >> 0x10U)),16);
    bufp->chgSData(oldp+1142,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x1bdU])),16);
    bufp->chgSData(oldp+1143,((vlSelfRef.fc_layer__DOT__weight_memory[0x1bdU] 
                               >> 0x10U)),16);
    bufp->chgSData(oldp+1144,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x1beU])),16);
    bufp->chgSData(oldp+1145,((vlSelfRef.fc_layer__DOT__weight_memory[0x1beU] 
                               >> 0x10U)),16);
    bufp->chgSData(oldp+1146,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x1bfU])),16);
    bufp->chgSData(oldp+1147,((vlSelfRef.fc_layer__DOT__weight_memory[0x1bfU] 
                               >> 0x10U)),16);
    bufp->chgSData(oldp+1148,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x1c0U])),16);
    bufp->chgSData(oldp+1149,((vlSelfRef.fc_layer__DOT__weight_memory[0x1c0U] 
                               >> 0x10U)),16);
    bufp->chgSData(oldp+1150,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x1c1U])),16);
    bufp->chgSData(oldp+1151,((vlSelfRef.fc_layer__DOT__weight_memory[0x1c1U] 
                               >> 0x10U)),16);
    bufp->chgSData(oldp+1152,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x1c2U])),16);
    bufp->chgSData(oldp+1153,((vlSelfRef.fc_layer__DOT__weight_memory[0x1c2U] 
                               >> 0x10U)),16);
    bufp->chgSData(oldp+1154,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x1c3U])),16);
    bufp->chgSData(oldp+1155,((vlSelfRef.fc_layer__DOT__weight_memory[0x1c3U] 
                               >> 0x10U)),16);
    bufp->chgSData(oldp+1156,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x1c4U])),16);
    bufp->chgSData(oldp+1157,((vlSelfRef.fc_layer__DOT__weight_memory[0x1c4U] 
                               >> 0x10U)),16);
    bufp->chgSData(oldp+1158,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x1c5U])),16);
    bufp->chgSData(oldp+1159,((vlSelfRef.fc_layer__DOT__weight_memory[0x1c5U] 
                               >> 0x10U)),16);
    bufp->chgSData(oldp+1160,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x1c6U])),16);
    bufp->chgSData(oldp+1161,((vlSelfRef.fc_layer__DOT__weight_memory[0x1c6U] 
                               >> 0x10U)),16);
    bufp->chgSData(oldp+1162,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x1c7U])),16);
    bufp->chgSData(oldp+1163,((vlSelfRef.fc_layer__DOT__weight_memory[0x1c7U] 
                               >> 0x10U)),16);
    bufp->chgSData(oldp+1164,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x1c8U])),16);
    bufp->chgSData(oldp+1165,((vlSelfRef.fc_layer__DOT__weight_memory[0x1c8U] 
                               >> 0x10U)),16);
    bufp->chgSData(oldp+1166,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x1c9U])),16);
    bufp->chgSData(oldp+1167,((vlSelfRef.fc_layer__DOT__weight_memory[0x1c9U] 
                               >> 0x10U)),16);
    bufp->chgSData(oldp+1168,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x1caU])),16);
    bufp->chgSData(oldp+1169,((vlSelfRef.fc_layer__DOT__weight_memory[0x1caU] 
                               >> 0x10U)),16);
    bufp->chgSData(oldp+1170,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x1cbU])),16);
    bufp->chgSData(oldp+1171,((vlSelfRef.fc_layer__DOT__weight_memory[0x1cbU] 
                               >> 0x10U)),16);
    bufp->chgSData(oldp+1172,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x1ccU])),16);
    bufp->chgSData(oldp+1173,((vlSelfRef.fc_layer__DOT__weight_memory[0x1ccU] 
                               >> 0x10U)),16);
    bufp->chgSData(oldp+1174,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x1cdU])),16);
    bufp->chgSData(oldp+1175,((vlSelfRef.fc_layer__DOT__weight_memory[0x1cdU] 
                               >> 0x10U)),16);
    bufp->chgSData(oldp+1176,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x1ceU])),16);
    bufp->chgSData(oldp+1177,((vlSelfRef.fc_layer__DOT__weight_memory[0x1ceU] 
                               >> 0x10U)),16);
    bufp->chgSData(oldp+1178,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x1cfU])),16);
    bufp->chgSData(oldp+1179,((vlSelfRef.fc_layer__DOT__weight_memory[0x1cfU] 
                               >> 0x10U)),16);
    bufp->chgSData(oldp+1180,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x1d0U])),16);
    bufp->chgSData(oldp+1181,((vlSelfRef.fc_layer__DOT__weight_memory[0x1d0U] 
                               >> 0x10U)),16);
    bufp->chgSData(oldp+1182,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x1d1U])),16);
    bufp->chgSData(oldp+1183,((vlSelfRef.fc_layer__DOT__weight_memory[0x1d1U] 
                               >> 0x10U)),16);
    bufp->chgSData(oldp+1184,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x1d2U])),16);
    bufp->chgSData(oldp+1185,((vlSelfRef.fc_layer__DOT__weight_memory[0x1d2U] 
                               >> 0x10U)),16);
    bufp->chgSData(oldp+1186,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x1d3U])),16);
    bufp->chgSData(oldp+1187,((vlSelfRef.fc_layer__DOT__weight_memory[0x1d3U] 
                               >> 0x10U)),16);
    bufp->chgSData(oldp+1188,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x1d4U])),16);
    bufp->chgSData(oldp+1189,((vlSelfRef.fc_layer__DOT__weight_memory[0x1d4U] 
                               >> 0x10U)),16);
    bufp->chgSData(oldp+1190,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x1d5U])),16);
    bufp->chgSData(oldp+1191,((vlSelfRef.fc_layer__DOT__weight_memory[0x1d5U] 
                               >> 0x10U)),16);
    bufp->chgSData(oldp+1192,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x1d6U])),16);
    bufp->chgSData(oldp+1193,((vlSelfRef.fc_layer__DOT__weight_memory[0x1d6U] 
                               >> 0x10U)),16);
    bufp->chgSData(oldp+1194,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x1d7U])),16);
    bufp->chgSData(oldp+1195,((vlSelfRef.fc_layer__DOT__weight_memory[0x1d7U] 
                               >> 0x10U)),16);
    bufp->chgSData(oldp+1196,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x1d8U])),16);
    bufp->chgSData(oldp+1197,((vlSelfRef.fc_layer__DOT__weight_memory[0x1d8U] 
                               >> 0x10U)),16);
    bufp->chgSData(oldp+1198,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x1d9U])),16);
    bufp->chgSData(oldp+1199,((vlSelfRef.fc_layer__DOT__weight_memory[0x1d9U] 
                               >> 0x10U)),16);
    bufp->chgSData(oldp+1200,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x1daU])),16);
    bufp->chgSData(oldp+1201,((vlSelfRef.fc_layer__DOT__weight_memory[0x1daU] 
                               >> 0x10U)),16);
    bufp->chgSData(oldp+1202,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x1dbU])),16);
    bufp->chgSData(oldp+1203,((vlSelfRef.fc_layer__DOT__weight_memory[0x1dbU] 
                               >> 0x10U)),16);
    bufp->chgSData(oldp+1204,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x1dcU])),16);
    bufp->chgSData(oldp+1205,((vlSelfRef.fc_layer__DOT__weight_memory[0x1dcU] 
                               >> 0x10U)),16);
    bufp->chgSData(oldp+1206,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x1ddU])),16);
    bufp->chgSData(oldp+1207,((vlSelfRef.fc_layer__DOT__weight_memory[0x1ddU] 
                               >> 0x10U)),16);
    bufp->chgSData(oldp+1208,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x1deU])),16);
    bufp->chgSData(oldp+1209,((vlSelfRef.fc_layer__DOT__weight_memory[0x1deU] 
                               >> 0x10U)),16);
    bufp->chgSData(oldp+1210,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x1dfU])),16);
    bufp->chgSData(oldp+1211,((vlSelfRef.fc_layer__DOT__weight_memory[0x1dfU] 
                               >> 0x10U)),16);
    bufp->chgSData(oldp+1212,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x1e0U])),16);
    bufp->chgSData(oldp+1213,((vlSelfRef.fc_layer__DOT__weight_memory[0x1e0U] 
                               >> 0x10U)),16);
    bufp->chgSData(oldp+1214,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x1e1U])),16);
    bufp->chgSData(oldp+1215,((vlSelfRef.fc_layer__DOT__weight_memory[0x1e1U] 
                               >> 0x10U)),16);
    bufp->chgSData(oldp+1216,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x1e2U])),16);
    bufp->chgSData(oldp+1217,((vlSelfRef.fc_layer__DOT__weight_memory[0x1e2U] 
                               >> 0x10U)),16);
    bufp->chgSData(oldp+1218,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x1e3U])),16);
    bufp->chgSData(oldp+1219,((vlSelfRef.fc_layer__DOT__weight_memory[0x1e3U] 
                               >> 0x10U)),16);
    bufp->chgSData(oldp+1220,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x1e4U])),16);
    bufp->chgSData(oldp+1221,((vlSelfRef.fc_layer__DOT__weight_memory[0x1e4U] 
                               >> 0x10U)),16);
    bufp->chgSData(oldp+1222,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x1e5U])),16);
    bufp->chgSData(oldp+1223,((vlSelfRef.fc_layer__DOT__weight_memory[0x1e5U] 
                               >> 0x10U)),16);
    bufp->chgSData(oldp+1224,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x1e6U])),16);
    bufp->chgSData(oldp+1225,((vlSelfRef.fc_layer__DOT__weight_memory[0x1e6U] 
                               >> 0x10U)),16);
    bufp->chgSData(oldp+1226,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x1e7U])),16);
    bufp->chgSData(oldp+1227,((vlSelfRef.fc_layer__DOT__weight_memory[0x1e7U] 
                               >> 0x10U)),16);
    bufp->chgSData(oldp+1228,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x1e8U])),16);
    bufp->chgSData(oldp+1229,((vlSelfRef.fc_layer__DOT__weight_memory[0x1e8U] 
                               >> 0x10U)),16);
    bufp->chgSData(oldp+1230,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x1e9U])),16);
    bufp->chgSData(oldp+1231,((vlSelfRef.fc_layer__DOT__weight_memory[0x1e9U] 
                               >> 0x10U)),16);
    bufp->chgSData(oldp+1232,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x1eaU])),16);
    bufp->chgSData(oldp+1233,((vlSelfRef.fc_layer__DOT__weight_memory[0x1eaU] 
                               >> 0x10U)),16);
    bufp->chgSData(oldp+1234,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x1ebU])),16);
    bufp->chgSData(oldp+1235,((vlSelfRef.fc_layer__DOT__weight_memory[0x1ebU] 
                               >> 0x10U)),16);
    bufp->chgSData(oldp+1236,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x1ecU])),16);
    bufp->chgSData(oldp+1237,((vlSelfRef.fc_layer__DOT__weight_memory[0x1ecU] 
                               >> 0x10U)),16);
    bufp->chgSData(oldp+1238,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x1edU])),16);
    bufp->chgSData(oldp+1239,((vlSelfRef.fc_layer__DOT__weight_memory[0x1edU] 
                               >> 0x10U)),16);
    bufp->chgSData(oldp+1240,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x1eeU])),16);
    bufp->chgSData(oldp+1241,((vlSelfRef.fc_layer__DOT__weight_memory[0x1eeU] 
                               >> 0x10U)),16);
    bufp->chgSData(oldp+1242,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x1efU])),16);
    bufp->chgSData(oldp+1243,((vlSelfRef.fc_layer__DOT__weight_memory[0x1efU] 
                               >> 0x10U)),16);
    bufp->chgSData(oldp+1244,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x1f0U])),16);
    bufp->chgSData(oldp+1245,((vlSelfRef.fc_layer__DOT__weight_memory[0x1f0U] 
                               >> 0x10U)),16);
    bufp->chgSData(oldp+1246,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x1f1U])),16);
    bufp->chgSData(oldp+1247,((vlSelfRef.fc_layer__DOT__weight_memory[0x1f1U] 
                               >> 0x10U)),16);
    bufp->chgSData(oldp+1248,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x1f2U])),16);
    bufp->chgSData(oldp+1249,((vlSelfRef.fc_layer__DOT__weight_memory[0x1f2U] 
                               >> 0x10U)),16);
    bufp->chgSData(oldp+1250,((0xffffU & vlSelfRef.fc_layer__DOT__weight_memory[0x1f3U])),16);
    bufp->chgSData(oldp+1251,((vlSelfRef.fc_layer__DOT__weight_memory[0x1f3U] 
                               >> 0x10U)),16);
    bufp->chgSData(oldp+1252,((0xffffU & vlSelfRef.fc_layer__DOT__bias_memory[0U])),16);
    bufp->chgSData(oldp+1253,((vlSelfRef.fc_layer__DOT__bias_memory[0U] 
                               >> 0x10U)),16);
    bufp->chgSData(oldp+1254,((0xffffU & vlSelfRef.fc_layer__DOT__bias_memory[1U])),16);
    bufp->chgSData(oldp+1255,((vlSelfRef.fc_layer__DOT__bias_memory[1U] 
                               >> 0x10U)),16);
    bufp->chgSData(oldp+1256,((0xffffU & vlSelfRef.fc_layer__DOT__bias_memory[2U])),16);
    bufp->chgSData(oldp+1257,((vlSelfRef.fc_layer__DOT__bias_memory[2U] 
                               >> 0x10U)),16);
    bufp->chgSData(oldp+1258,((0xffffU & vlSelfRef.fc_layer__DOT__bias_memory[3U])),16);
    bufp->chgSData(oldp+1259,((vlSelfRef.fc_layer__DOT__bias_memory[3U] 
                               >> 0x10U)),16);
    bufp->chgSData(oldp+1260,((0xffffU & vlSelfRef.fc_layer__DOT__bias_memory[4U])),16);
    bufp->chgSData(oldp+1261,((vlSelfRef.fc_layer__DOT__bias_memory[4U] 
                               >> 0x10U)),16);
    bufp->chgSData(oldp+1262,((0xffffU & vlSelfRef.fc_layer__DOT__input_reg[0U])),16);
    bufp->chgSData(oldp+1263,((vlSelfRef.fc_layer__DOT__input_reg[0U] 
                               >> 0x10U)),16);
    bufp->chgSData(oldp+1264,((0xffffU & vlSelfRef.fc_layer__DOT__input_reg[1U])),16);
    bufp->chgSData(oldp+1265,((vlSelfRef.fc_layer__DOT__input_reg[1U] 
                               >> 0x10U)),16);
    bufp->chgSData(oldp+1266,((0xffffU & vlSelfRef.fc_layer__DOT__input_reg[2U])),16);
    bufp->chgSData(oldp+1267,((vlSelfRef.fc_layer__DOT__input_reg[2U] 
                               >> 0x10U)),16);
    bufp->chgSData(oldp+1268,((0xffffU & vlSelfRef.fc_layer__DOT__input_reg[3U])),16);
    bufp->chgSData(oldp+1269,((vlSelfRef.fc_layer__DOT__input_reg[3U] 
                               >> 0x10U)),16);
    bufp->chgSData(oldp+1270,((0xffffU & vlSelfRef.fc_layer__DOT__input_reg[4U])),16);
    bufp->chgSData(oldp+1271,((vlSelfRef.fc_layer__DOT__input_reg[4U] 
                               >> 0x10U)),16);
    bufp->chgSData(oldp+1272,((0xffffU & vlSelfRef.fc_layer__DOT__input_reg[5U])),16);
    bufp->chgSData(oldp+1273,((vlSelfRef.fc_layer__DOT__input_reg[5U] 
                               >> 0x10U)),16);
    bufp->chgSData(oldp+1274,((0xffffU & vlSelfRef.fc_layer__DOT__input_reg[6U])),16);
    bufp->chgSData(oldp+1275,((vlSelfRef.fc_layer__DOT__input_reg[6U] 
                               >> 0x10U)),16);
    bufp->chgSData(oldp+1276,((0xffffU & vlSelfRef.fc_layer__DOT__input_reg[7U])),16);
    bufp->chgSData(oldp+1277,((vlSelfRef.fc_layer__DOT__input_reg[7U] 
                               >> 0x10U)),16);
    bufp->chgSData(oldp+1278,((0xffffU & vlSelfRef.fc_layer__DOT__input_reg[8U])),16);
    bufp->chgSData(oldp+1279,((vlSelfRef.fc_layer__DOT__input_reg[8U] 
                               >> 0x10U)),16);
    bufp->chgSData(oldp+1280,((0xffffU & vlSelfRef.fc_layer__DOT__input_reg[9U])),16);
    bufp->chgSData(oldp+1281,((vlSelfRef.fc_layer__DOT__input_reg[9U] 
                               >> 0x10U)),16);
    bufp->chgSData(oldp+1282,((0xffffU & vlSelfRef.fc_layer__DOT__input_reg[0xaU])),16);
    bufp->chgSData(oldp+1283,((vlSelfRef.fc_layer__DOT__input_reg[0xaU] 
                               >> 0x10U)),16);
    bufp->chgSData(oldp+1284,((0xffffU & vlSelfRef.fc_layer__DOT__input_reg[0xbU])),16);
    bufp->chgSData(oldp+1285,((vlSelfRef.fc_layer__DOT__input_reg[0xbU] 
                               >> 0x10U)),16);
    bufp->chgSData(oldp+1286,((0xffffU & vlSelfRef.fc_layer__DOT__input_reg[0xcU])),16);
    bufp->chgSData(oldp+1287,((vlSelfRef.fc_layer__DOT__input_reg[0xcU] 
                               >> 0x10U)),16);
    bufp->chgSData(oldp+1288,((0xffffU & vlSelfRef.fc_layer__DOT__input_reg[0xdU])),16);
    bufp->chgSData(oldp+1289,((vlSelfRef.fc_layer__DOT__input_reg[0xdU] 
                               >> 0x10U)),16);
    bufp->chgSData(oldp+1290,((0xffffU & vlSelfRef.fc_layer__DOT__input_reg[0xeU])),16);
    bufp->chgSData(oldp+1291,((vlSelfRef.fc_layer__DOT__input_reg[0xeU] 
                               >> 0x10U)),16);
    bufp->chgSData(oldp+1292,((0xffffU & vlSelfRef.fc_layer__DOT__input_reg[0xfU])),16);
    bufp->chgSData(oldp+1293,((vlSelfRef.fc_layer__DOT__input_reg[0xfU] 
                               >> 0x10U)),16);
    bufp->chgSData(oldp+1294,((0xffffU & vlSelfRef.fc_layer__DOT__input_reg[0x10U])),16);
    bufp->chgSData(oldp+1295,((vlSelfRef.fc_layer__DOT__input_reg[0x10U] 
                               >> 0x10U)),16);
    bufp->chgSData(oldp+1296,((0xffffU & vlSelfRef.fc_layer__DOT__input_reg[0x11U])),16);
    bufp->chgSData(oldp+1297,((vlSelfRef.fc_layer__DOT__input_reg[0x11U] 
                               >> 0x10U)),16);
    bufp->chgSData(oldp+1298,((0xffffU & vlSelfRef.fc_layer__DOT__input_reg[0x12U])),16);
    bufp->chgSData(oldp+1299,((vlSelfRef.fc_layer__DOT__input_reg[0x12U] 
                               >> 0x10U)),16);
    bufp->chgSData(oldp+1300,((0xffffU & vlSelfRef.fc_layer__DOT__input_reg[0x13U])),16);
    bufp->chgSData(oldp+1301,((vlSelfRef.fc_layer__DOT__input_reg[0x13U] 
                               >> 0x10U)),16);
    bufp->chgSData(oldp+1302,((0xffffU & vlSelfRef.fc_layer__DOT__input_reg[0x14U])),16);
    bufp->chgSData(oldp+1303,((vlSelfRef.fc_layer__DOT__input_reg[0x14U] 
                               >> 0x10U)),16);
    bufp->chgSData(oldp+1304,((0xffffU & vlSelfRef.fc_layer__DOT__input_reg[0x15U])),16);
    bufp->chgSData(oldp+1305,((vlSelfRef.fc_layer__DOT__input_reg[0x15U] 
                               >> 0x10U)),16);
    bufp->chgSData(oldp+1306,((0xffffU & vlSelfRef.fc_layer__DOT__input_reg[0x16U])),16);
    bufp->chgSData(oldp+1307,((vlSelfRef.fc_layer__DOT__input_reg[0x16U] 
                               >> 0x10U)),16);
    bufp->chgSData(oldp+1308,((0xffffU & vlSelfRef.fc_layer__DOT__input_reg[0x17U])),16);
    bufp->chgSData(oldp+1309,((vlSelfRef.fc_layer__DOT__input_reg[0x17U] 
                               >> 0x10U)),16);
    bufp->chgSData(oldp+1310,((0xffffU & vlSelfRef.fc_layer__DOT__input_reg[0x18U])),16);
    bufp->chgSData(oldp+1311,((vlSelfRef.fc_layer__DOT__input_reg[0x18U] 
                               >> 0x10U)),16);
    bufp->chgSData(oldp+1312,((0xffffU & vlSelfRef.fc_layer__DOT__input_reg[0x19U])),16);
    bufp->chgSData(oldp+1313,((vlSelfRef.fc_layer__DOT__input_reg[0x19U] 
                               >> 0x10U)),16);
    bufp->chgSData(oldp+1314,((0xffffU & vlSelfRef.fc_layer__DOT__input_reg[0x1aU])),16);
    bufp->chgSData(oldp+1315,((vlSelfRef.fc_layer__DOT__input_reg[0x1aU] 
                               >> 0x10U)),16);
    bufp->chgSData(oldp+1316,((0xffffU & vlSelfRef.fc_layer__DOT__input_reg[0x1bU])),16);
    bufp->chgSData(oldp+1317,((vlSelfRef.fc_layer__DOT__input_reg[0x1bU] 
                               >> 0x10U)),16);
    bufp->chgSData(oldp+1318,((0xffffU & vlSelfRef.fc_layer__DOT__input_reg[0x1cU])),16);
    bufp->chgSData(oldp+1319,((vlSelfRef.fc_layer__DOT__input_reg[0x1cU] 
                               >> 0x10U)),16);
    bufp->chgSData(oldp+1320,((0xffffU & vlSelfRef.fc_layer__DOT__input_reg[0x1dU])),16);
    bufp->chgSData(oldp+1321,((vlSelfRef.fc_layer__DOT__input_reg[0x1dU] 
                               >> 0x10U)),16);
    bufp->chgSData(oldp+1322,((0xffffU & vlSelfRef.fc_layer__DOT__input_reg[0x1eU])),16);
    bufp->chgSData(oldp+1323,((vlSelfRef.fc_layer__DOT__input_reg[0x1eU] 
                               >> 0x10U)),16);
    bufp->chgSData(oldp+1324,((0xffffU & vlSelfRef.fc_layer__DOT__input_reg[0x1fU])),16);
    bufp->chgSData(oldp+1325,((vlSelfRef.fc_layer__DOT__input_reg[0x1fU] 
                               >> 0x10U)),16);
    bufp->chgSData(oldp+1326,((0xffffU & vlSelfRef.fc_layer__DOT__input_reg[0x20U])),16);
    bufp->chgSData(oldp+1327,((vlSelfRef.fc_layer__DOT__input_reg[0x20U] 
                               >> 0x10U)),16);
    bufp->chgSData(oldp+1328,((0xffffU & vlSelfRef.fc_layer__DOT__input_reg[0x21U])),16);
    bufp->chgSData(oldp+1329,((vlSelfRef.fc_layer__DOT__input_reg[0x21U] 
                               >> 0x10U)),16);
    bufp->chgSData(oldp+1330,((0xffffU & vlSelfRef.fc_layer__DOT__input_reg[0x22U])),16);
    bufp->chgSData(oldp+1331,((vlSelfRef.fc_layer__DOT__input_reg[0x22U] 
                               >> 0x10U)),16);
    bufp->chgSData(oldp+1332,((0xffffU & vlSelfRef.fc_layer__DOT__input_reg[0x23U])),16);
    bufp->chgSData(oldp+1333,((vlSelfRef.fc_layer__DOT__input_reg[0x23U] 
                               >> 0x10U)),16);
    bufp->chgSData(oldp+1334,((0xffffU & vlSelfRef.fc_layer__DOT__input_reg[0x24U])),16);
    bufp->chgSData(oldp+1335,((vlSelfRef.fc_layer__DOT__input_reg[0x24U] 
                               >> 0x10U)),16);
    bufp->chgSData(oldp+1336,((0xffffU & vlSelfRef.fc_layer__DOT__input_reg[0x25U])),16);
    bufp->chgSData(oldp+1337,((vlSelfRef.fc_layer__DOT__input_reg[0x25U] 
                               >> 0x10U)),16);
    bufp->chgSData(oldp+1338,((0xffffU & vlSelfRef.fc_layer__DOT__input_reg[0x26U])),16);
    bufp->chgSData(oldp+1339,((vlSelfRef.fc_layer__DOT__input_reg[0x26U] 
                               >> 0x10U)),16);
    bufp->chgSData(oldp+1340,((0xffffU & vlSelfRef.fc_layer__DOT__input_reg[0x27U])),16);
    bufp->chgSData(oldp+1341,((vlSelfRef.fc_layer__DOT__input_reg[0x27U] 
                               >> 0x10U)),16);
    bufp->chgSData(oldp+1342,((0xffffU & vlSelfRef.fc_layer__DOT__input_reg[0x28U])),16);
    bufp->chgSData(oldp+1343,((vlSelfRef.fc_layer__DOT__input_reg[0x28U] 
                               >> 0x10U)),16);
    bufp->chgSData(oldp+1344,((0xffffU & vlSelfRef.fc_layer__DOT__input_reg[0x29U])),16);
    bufp->chgSData(oldp+1345,((vlSelfRef.fc_layer__DOT__input_reg[0x29U] 
                               >> 0x10U)),16);
    bufp->chgSData(oldp+1346,((0xffffU & vlSelfRef.fc_layer__DOT__input_reg[0x2aU])),16);
    bufp->chgSData(oldp+1347,((vlSelfRef.fc_layer__DOT__input_reg[0x2aU] 
                               >> 0x10U)),16);
    bufp->chgSData(oldp+1348,((0xffffU & vlSelfRef.fc_layer__DOT__input_reg[0x2bU])),16);
    bufp->chgSData(oldp+1349,((vlSelfRef.fc_layer__DOT__input_reg[0x2bU] 
                               >> 0x10U)),16);
    bufp->chgSData(oldp+1350,((0xffffU & vlSelfRef.fc_layer__DOT__input_reg[0x2cU])),16);
    bufp->chgSData(oldp+1351,((vlSelfRef.fc_layer__DOT__input_reg[0x2cU] 
                               >> 0x10U)),16);
    bufp->chgSData(oldp+1352,((0xffffU & vlSelfRef.fc_layer__DOT__input_reg[0x2dU])),16);
    bufp->chgSData(oldp+1353,((vlSelfRef.fc_layer__DOT__input_reg[0x2dU] 
                               >> 0x10U)),16);
    bufp->chgSData(oldp+1354,((0xffffU & vlSelfRef.fc_layer__DOT__input_reg[0x2eU])),16);
    bufp->chgSData(oldp+1355,((vlSelfRef.fc_layer__DOT__input_reg[0x2eU] 
                               >> 0x10U)),16);
    bufp->chgSData(oldp+1356,((0xffffU & vlSelfRef.fc_layer__DOT__input_reg[0x2fU])),16);
    bufp->chgSData(oldp+1357,((vlSelfRef.fc_layer__DOT__input_reg[0x2fU] 
                               >> 0x10U)),16);
    bufp->chgSData(oldp+1358,((0xffffU & vlSelfRef.fc_layer__DOT__input_reg[0x30U])),16);
    bufp->chgSData(oldp+1359,((vlSelfRef.fc_layer__DOT__input_reg[0x30U] 
                               >> 0x10U)),16);
    bufp->chgSData(oldp+1360,((0xffffU & vlSelfRef.fc_layer__DOT__input_reg[0x31U])),16);
    bufp->chgSData(oldp+1361,((vlSelfRef.fc_layer__DOT__input_reg[0x31U] 
                               >> 0x10U)),16);
    bufp->chgSData(oldp+1362,((0xffffU & vlSelfRef.fc_layer__DOT__output_reg[0U])),16);
    bufp->chgSData(oldp+1363,((vlSelfRef.fc_layer__DOT__output_reg[0U] 
                               >> 0x10U)),16);
    bufp->chgSData(oldp+1364,((0xffffU & vlSelfRef.fc_layer__DOT__output_reg[1U])),16);
    bufp->chgSData(oldp+1365,((vlSelfRef.fc_layer__DOT__output_reg[1U] 
                               >> 0x10U)),16);
    bufp->chgSData(oldp+1366,((0xffffU & vlSelfRef.fc_layer__DOT__output_reg[2U])),16);
    bufp->chgSData(oldp+1367,((vlSelfRef.fc_layer__DOT__output_reg[2U] 
                               >> 0x10U)),16);
    bufp->chgSData(oldp+1368,((0xffffU & vlSelfRef.fc_layer__DOT__output_reg[3U])),16);
    bufp->chgSData(oldp+1369,((vlSelfRef.fc_layer__DOT__output_reg[3U] 
                               >> 0x10U)),16);
    bufp->chgSData(oldp+1370,((0xffffU & vlSelfRef.fc_layer__DOT__output_reg[4U])),16);
    bufp->chgSData(oldp+1371,((vlSelfRef.fc_layer__DOT__output_reg[4U] 
                               >> 0x10U)),16);
    bufp->chgSData(oldp+1372,((0xffffU & vlSelfRef.fc_layer__DOT__output_reg_next[0U])),16);
    bufp->chgSData(oldp+1373,((vlSelfRef.fc_layer__DOT__output_reg_next[0U] 
                               >> 0x10U)),16);
    bufp->chgSData(oldp+1374,((0xffffU & vlSelfRef.fc_layer__DOT__output_reg_next[1U])),16);
    bufp->chgSData(oldp+1375,((vlSelfRef.fc_layer__DOT__output_reg_next[1U] 
                               >> 0x10U)),16);
    bufp->chgSData(oldp+1376,((0xffffU & vlSelfRef.fc_layer__DOT__output_reg_next[2U])),16);
    bufp->chgSData(oldp+1377,((vlSelfRef.fc_layer__DOT__output_reg_next[2U] 
                               >> 0x10U)),16);
    bufp->chgSData(oldp+1378,((0xffffU & vlSelfRef.fc_layer__DOT__output_reg_next[3U])),16);
    bufp->chgSData(oldp+1379,((vlSelfRef.fc_layer__DOT__output_reg_next[3U] 
                               >> 0x10U)),16);
    bufp->chgSData(oldp+1380,((0xffffU & vlSelfRef.fc_layer__DOT__output_reg_next[4U])),16);
    bufp->chgSData(oldp+1381,((vlSelfRef.fc_layer__DOT__output_reg_next[4U] 
                               >> 0x10U)),16);
    bufp->chgCData(oldp+1382,(vlSelfRef.fc_layer__DOT__current_state),3);
    bufp->chgCData(oldp+1383,(vlSelfRef.fc_layer__DOT__next_state),3);
    bufp->chgSData(oldp+1384,(vlSelfRef.fc_layer__DOT__input_counter),10);
    bufp->chgSData(oldp+1385,(vlSelfRef.fc_layer__DOT__output_counter),10);
    bufp->chgSData(oldp+1386,(vlSelfRef.fc_layer__DOT__input_counter_next),10);
    bufp->chgSData(oldp+1387,(vlSelfRef.fc_layer__DOT__output_counter_next),10);
    bufp->chgIData(oldp+1388,(vlSelfRef.fc_layer__DOT__mult_result_full),32);
    bufp->chgSData(oldp+1389,(vlSelfRef.fc_layer__DOT__mult_result),16);
    bufp->chgQData(oldp+1390,(vlSelfRef.fc_layer__DOT__accumulator),42);
    bufp->chgQData(oldp+1392,(vlSelfRef.fc_layer__DOT__accumulator_next),42);
    bufp->chgSData(oldp+1394,(vlSelfRef.fc_layer__DOT__final_result),16);
    bufp->chgBit(oldp+1395,(vlSelfRef.fc_layer__DOT__computation_done));
    bufp->chgBit(oldp+1396,(vlSelfRef.fc_layer__DOT__weight_loading_done));
    bufp->chgBit(oldp+1397,(vlSelfRef.fc_layer__DOT__bias_loading_done));
    bufp->chgBit(oldp+1398,(vlSelfRef.fc_layer__DOT__overflow_flag));
    bufp->chgBit(oldp+1399,(vlSelfRef.fc_layer__DOT__underflow_flag));
    bufp->chgIData(oldp+1400,(vlSelfRef.fc_layer__DOT__unnamedblk1__DOT__i),32);
    bufp->chgIData(oldp+1401,(vlSelfRef.fc_layer__DOT__unnamedblk1__DOT__unnamedblk2__DOT__j),32);
    bufp->chgIData(oldp+1402,(vlSelfRef.fc_layer__DOT__unnamedblk3__DOT__j),32);
    bufp->chgCData(oldp+1403,(vlSelfRef.fc_layer__DOT__unnamedblk4__DOT__input_idx),7);
    bufp->chgCData(oldp+1404,(vlSelfRef.fc_layer__DOT__unnamedblk4__DOT__output_idx),4);
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
