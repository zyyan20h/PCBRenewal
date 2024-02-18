import matplotlib.pyplot as plt

class point_grapher():
    def plot_point(x, y, color):
        plt.plot(x, y,marker = 'o', color = color)

    def set_fig_name(name):
        plt.figure(name)

    def plot_track(st, en, track_layer, axes = plt):
        track_color = "red" if track_layer == "F.Cu" else "blue"

        axes.plot([st[0], en[0]], [st[1], en[1]], marker = 'o', label = track_layer, color = track_color)
        #point_grapher.plot_point(st[0], st[1], color = "green")
    


    def adjust_axes(axis= plt):
        #plt.legend()

        #FIX THIS
        # USE EDGE CUTS BORDER INSTEAD OF HARDCODING
        axis.set_xlim([15000000, 50000000])
        axis.set_ylim([30000000, 48000000])

        axis.invert_yaxis()
        
        # .show()


    def stupid_print(s):
        plt.plot(0,0,label = s)
        plt.legend()
        plt.show()

    #def invert_axes():

