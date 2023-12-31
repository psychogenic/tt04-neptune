`default_nettype none
`timescale 1ns/1ps

/*
this testbench just instantiates the module and makes some convenient wires
that can be driven / tested by the cocotb test.py
*/

// testbench is controlled by test.py
module tb (
    input [2:0] clk_config,
    input input_pulse,
    input display_single_enable,
    input display_single_select,
    output [6:0] segments,
    output prox_select
    );

    // this part dumps the trace to a vcd file that can be viewed with GTKWave
    initial begin
        $dumpfile ("tb.vcd");
        $dumpvars (0, tb);
        #1;
    end

    // wire up the inputs and outputs
    reg  clk;
    reg  rst_n;
    reg  ena;
    // reg  [7:0] ui_in;
    reg  [7:0] uio_in;
    wire [7:0] uo_out;
    wire [7:0] uio_out;
    wire [7:0] uio_oe;
    
    assign prox_select = uo_out[7];
    assign segments = uo_out[6:0];
    
    wire [7:0] ui_in2 = 8'b11110111;
    wire [7:0] ui_in = {display_single_select, 
                        display_single_enable, 
                        input_pulse, 
                        clk_config[2], clk_config[1], clk_config[0],
                        1'b0,1'b0};

    tt_um_psychogenic_neptuneproportional tt_um_psychogenic_neptuneproportional(
    // include power ports for the Gate Level test
    `ifdef GL_TEST
        .VPWR( 1'b1),
        .VGND( 1'b0),
    `endif
        .ui_in      (ui_in),    // Dedicated inputs
        .uo_out     (uo_out),   // Dedicated outputs
        .uio_in     (uio_in),   // IOs: Input path
        .uio_out    (uio_out),  // IOs: Output path
        .uio_oe     (uio_oe),   // IOs: Enable path (active high: 0=input, 1=output)
        .ena        (ena),      // enable - goes high when design is selected
        .clk        (clk),      // clock
        .rst_n      (rst_n)     // not reset
        );

endmodule
