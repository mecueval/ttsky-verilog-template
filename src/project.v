/*
 * Copyright (c) 2024 Maria Emilia Cueva
 * SPDX-License-Identifier: Apache-2.0
 */

`default_nettype none

module tt_um_example (
    input  wire [7:0] ui_in,    // Dedicated inputs
    output wire [7:0] uo_out,   // Dedicated outputs
    input  wire [7:0] uio_in,   // IOs: Input path
    output wire [7:0] uio_out,  // IOs: Output path
    output wire [7:0] uio_oe,   // IOs: Enable path (active high: 0=input, 1=output)
    input  wire       ena,      // always 1 when the design is powered, so you can ignore it
    input  wire       clk,      // clock
    input  wire       rst_n     // reset_n - low to reset
);


  wire rst = ~rst_n;

  // Asignación de entradas del juego
  wire [3:0] guess   = ui_in[3:0];   // 4 bits para el número que se adivina
  wire       verify  = ui_in[4];     // Botón de verificar intento
  wire       new_game = ui_in[5];    // Botón de nuevo juego

  // Salidas del juego
  wire [2:0] hint;
  wire       correct;
  wire [1:0] attempts_left;

  // Instancia del módulo principal
  guess_number game_inst (
    .clk(clk),
    .rst(rst),
    .guess(guess),
    .verify(verify),
    .new_game(new_game),
    .hint(hint),
    .correct(correct),
    .attempts_left(attempts_left)
  );

  // Asignar salidas a los pines dedicados
  assign uo_out[2:0] = hint;               // Pistas: bit2=correcto, bit1=más alto, bit0=más bajo
  assign uo_out[3]   = correct;            // LED de acierto (redundante con hint[2])
  assign uo_out[5:4] = attempts_left;      // Intentos restantes (2 bits)
  assign uo_out[7:6] = 2'b00;              // Salidas no usadas a 0

  // Configurar pines bidireccionales como entrada (alta impedancia)
  assign uio_out = 8'b0;
  assign uio_oe  = 8'b0;

  // Evitar warnings de señales no usadas
  wire _unused = &{ena, uio_in, 1'b0};

endmodule
