module guess_number (
    input wire clk,
    input wire rst,
    input wire [3:0] guess,
    input wire verify,
    input wire new_game,
    output reg [2:0] hint,
    output wire correct,
    output wire [1:0] attempts_left
);

localparam WAIT_VERIFY = 1'b0;
localparam GAME_OVER = 1'b1;

reg state;
reg [3:0] secret_number;
reg [1:0] attempts_left_reg;
reg [3:0] lfsr;
reg verify_prev;
reg new_game_prev;

// Detectores de flanco 
wire verify_edge = verify & ~verify_prev;
wire new_game_edge = new_game & ~new_game_prev;

always @(posedge clk or posedge rst) begin
    if (rst) begin
        verify_prev <= 0;
        new_game_prev <= 0;
        lfsr <= 4'b1011; 
        state <= WAIT_VERIFY;
        secret_number <= 4'b0110;
        attempts_left_reg <= 2'b11;
        hint <= 0;
    end else begin
        verify_prev <= verify;
        new_game_prev <= new_game;
        
        
        lfsr <= {lfsr[2:0], lfsr[3] ^ lfsr[1]}; 
      
        if (new_game_edge) begin
            secret_number <= lfsr; 
            attempts_left_reg <= 2'b11;
            state <= WAIT_VERIFY;
            hint <= 0;
        end else if (state == WAIT_VERIFY && verify_edge) begin
            if (guess == secret_number) begin
                hint <= 3'b100;
                state <= GAME_OVER;
            end else begin
                // Pista
                if (guess < secret_number)
                    hint <= 3'b010;
                else
                    hint <= 3'b001;

                if (attempts_left_reg == 2'b01) begin
                    attempts_left_reg <= 0;
                    state <= GAME_OVER;
                end else begin
                    attempts_left_reg <= attempts_left_reg - 1;
                end
            end
        end
    end
end

assign correct = hint[2];
assign attempts_left = attempts_left_reg;

endmodule