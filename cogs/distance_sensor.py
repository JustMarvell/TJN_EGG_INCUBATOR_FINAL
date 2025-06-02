import discord
from discord.ext import commands
from discord import app_commands
import contrls.ds_ctrl as ds

async def setup(bot: commands.Bot) :
    await bot.add_cog(DistanceSensor(bot))
    
class DistanceSensor(commands.Cog) :
    def __init__(self, bot) :
        self.bot = bot
        
    @commands.hybrid_command()
    async def test_distance_sensor(self, ctx : commands.Context):
        """Test the distance sensor"""
        await ctx.send("Distance sensor test complete!")
        
    @commands.hybrid_command()
    async def get_distance(self, ctx : commands.Context):
        """Get the distance from the sensor"""
        # Call the get_distance function from ds_ctrl.py
        distance = await ds.get_distance()
        await ctx.send(distance)