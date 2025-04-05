def get_display_string(grid, orientation=0):
        output = []
        output.append(" " + "_ " * 9)
        if orientation == 0:
            r = grid.T[::-1]
            s = 4
            e = 2
        if orientation == 1:
            r = grid[::-1, ::-1]
            s = 8
            e = 4
        if orientation == 2:
            r = grid.T[:, ::-1]
            s = 1
            e = 8
        if orientation == 3:
            r = grid
            s = 2
            e = 1
        for col in r:
            output.append("\n|")
            for n in col:
                if n & s:
                    g = "⍛" if n & 64 else "_"
                else:
                    g = "○" if n & 64 else " "

                output.append(g)
                output.append("|" if n & e else " ")
        print("old")
        return "".join(output)


def get_display_string_pl(grid, player_positions = [], orientation=0):
        or_pos = []
        symbs = [("߸","•"), ("⍛","○"), ("⍙","∆"), ("⍚","◇"),]

     
        
        output = []
        output.append(" " + "_ " * 9)

        positions_dict = {}
        if orientation == 0:
            r = grid.T[::-1]
            s = 4
            e = 2
            or_pos = [(8-pos[1], pos[0]) for pos in player_positions] 
        if orientation == 1:
            r = grid[::-1, ::-1]
            s = 8
            e = 4
            or_pos = [(8-pos[0], 8 - pos[1]) for pos in player_positions]
        if orientation == 2:
            r = grid.T[:, ::-1]
            s = 1
            e = 8
            or_pos = [(pos[1], 8-pos[0]) for pos in player_positions]
        if orientation == 3:
            r = grid
            s = 2
            e = 1
            or_pos = [pos for pos in player_positions]


        d = {pos: symbs[i] for i,pos in enumerate(or_pos)}

        for i, col in enumerate(r):
            output.append("\n|")
            for j, q in enumerate(col):
                sou, nsou = "_", " "

                if (i, j) in d:
                    sou, nsou = d[(i, j)][0], d[(i, j)][1]

                if q & 128:
                    sou, nsou = "⨱","×"

                output.append(sou if q & s else nsou)
                output.append("|" if q & e else " ")
        return "".join(output)