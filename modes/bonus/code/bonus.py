from mpf.core.mode import Mode
from mpf.core.delays import DelayManager
from mpf.core.utility_functions import Util
# Modified Sept 24,2023 to used the dblbonus lamp to control bonus points
# Hot Tip only gives max bonus count of 19. If doublebonus then its 28 (19,000 or 28,000 points)
class Count(Mode):

    def mode_start(self, **kwargs):
        self.bonus_value = 1000
        self.count_down = self.player.bonus
        self.itstilted = self.player.my_tilted
        self.machine.events.post("bonus_code_starting_value_" + str(self.count_down))
        self.dblbonus = self.player.my_dblbonus_awarded
        self.prepare_bonus()

    def prepare_bonus(self):
        # Double bonus lamp on so give 2000 bonus points not 1000
        if self.dblbonus > 0:
            self.bonus_value = 2000 
        #if self.machine.game.tilted:
        if self.itstilted == 1:
            self.machine.events.post("bonus_code_tilt_stop")
            # self.player.bonus_multiplier = 1     # loose BM on tilt
            self.player.multiplier = 1
            self.player.bonus = 0 
            self.count_down = 0
            self.bonus_value = 0
            self.stop()
            return
        self.bonus_step()
        
    def bonus_step(self, future=None, **kwargs):
        if self.count_down == 0:
            self.bonus_pause() 
                   
        if self.dblbonus == 0 and self.count_down > 0:
            self.machine.events.post("bonus_code_step")   #1 chime
            
        if self.dblbonus >= 1 and self.count_down > 0:
            self.machine.events.post("bonus_code_doublestep") # Ring chime twice not once
            
        if self.count_down > 0:
            if self.count_down >= 10 and self.count_down <= 19:
                self.machine.lights['l_bonus10'].on()
                self.machine.lights['l_bonus20'].off()
            else:
                self.machine.lights['l_bonus10'].off()
                       
        if self.count_down == 9:
            self.machine.lights['l_bonus10'].off()
                
        if self.count_down % 10 != 0 :
            self.machine.lights['l_bonus' + str(self.count_down % 10)].on()
        
        if self.count_down > 0:
            self.delay.add(ms=500, callback=self.do_bonus_step)
        else:
            self.bonus_pause()        

    def do_bonus_step(self):
        self.machine.events.post("bonus_code_countdown_" + str(self.count_down))
        # self.player.score += self.bonus_value * self.player.bonus_multiplier
        self.player.score += self.bonus_value * self.player.multiplier
        if self.count_down == 10:
            self.machine.lights['l_bonus10'].off()
            self.machine.events.post("play_1000_pts")
        if self.count_down == 20:
            self.machine.lights['l_bonus20'].off()
            self.machine.events.post("play_1000_pts")
        if self.count_down == 30:
            self.machine.lights['l_bonus10'].off()
            self.machine.events.post("play_1000_pts")
        
        if self.count_down % 10 != 0:
            self.machine.lights['l_bonus' + str(self.count_down % 10)].off()
            self.machine.events.post("play_1000_pts")
        self.count_down -= 1 
        # Set player.bonus so playfield show can light correct lamps
        self.player.bonus = self.count_down
        self.bonus_step()
        
    def bonus_pause(self):
        self.delay.add(ms=1000, callback=self.bonus_done)

    def bonus_done(self):
        self.machine.events.post("bonus_complete")
        self.player.bonus = 0
        if self.player.keepBM == 0:  # this means bonus mode has been called from ball_drain
            self.player.bonus_multiplier = 1  # don't want to reset if called from bullseye
        self.stop()
