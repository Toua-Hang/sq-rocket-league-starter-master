# Import necessary modules and functions
from turtle import speed
from util.objects import *
from util.routines import *
from util.tools import find_hits


# Define the Bot class that inherits from GoslingAgent
class Bot(GoslingAgent):
    def run(self):
        # Print debug information
        self.print_debug()

        # Get the current intent
        intent = self.get_intent()

        # If an intent is already set, print the debug information related to the intent and return
        if intent is not None:
            self.debug_intent()
            return

        # If it's the kickoff, set the intent to kickoff and return
        if self.kickoff_flag:
            self.set_intent(kickoff())
            return

        # If the bot is in front of the ball, set the intent to retreat to the friend's goal and return
        if self.is_in_front_of_ball():
            self.set_intent(goto(self.friend_goal.location))
            self.debug_text = "retreating"
            return

        # If the bot has enough boost (more than 99), set the intent to shoot at the foe's goal and return
        if self.me.boost > 99:
            self.set_intent(short_shot(self.foe_goal.location))
            self.debug_text = "shooting"
            return

        # Find the closest large boost pad and set the intent to go there and return
        target_boost = self.get_closest_large_boost()
        if target_boost:
            self.set_intent(goto(target_boost.location))
            self.debug_text = "getting boost"
            return

        # Calculate distances from the ball and the bot to the foe's goal and check if the bot is in front of the ball
        d1 = abs(self.ball.location.y - self.for_goal.location.y)
        d2 = abs(self.me.location.y - self.for_goal.location.y)
        is_in_front_of_ball = d1 > d2

        # If the bot has no intent and it's not the kickoff
        # Check if there are hits towards the opponent's goal or away from our own goal
        # Set the intent accordingly and print debug information
        if intent is None:
            targets = {
                "at_opponent_goal": (self.foe_goal.left_post, self.foe_goal.right_post),
                "away_from_our_net": (
                    self.friend_goal.right_post,
                    self.friend_goal.left_post,
                ),
            }
            hits = find_hits(self, targets)
            if len(hits["at_opponent_goal"]) > 0:
                self.set_intent(hits["at_opponent_goal"][0])
                self.debug_text = "at their goal"
                return
            if len(hits["away_from_our_net"]) > 0:
                print("away from our goal")
                self.set_intent(hits["away_from_our_net"][0])
                return

        # If the bot has enough boost (more than 90), set the intent to shoot at the foe's goal and return
        if self.me.boost > 90:
            self.set_intent(short_shot(self.foe_goal.location))
            return

        # Find available large boost pads, find the closest one, and set the intent to go there and return
        available_boosts = [
            boost for boost in self.boosts if boost.large and boost.active
        ]
        closest_boost = min(
            available_boosts,
            key=lambda boost: (self.me.location - boost.location).magnitude(),
            default=None,
        )
        if closest_boost:
            self.set_intent(goto(closest_boost.location))
            return

        # If none of the previous conditions are met, set the intent to kickoff and return
        self.set_intent(kickoff())
