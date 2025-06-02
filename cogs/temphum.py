import discord
from discord.ext import commands
from discord import app_commands
import contrls.th_ctrl as th

async def setup(bot: commands.Bot) :
    await bot.add_cog(TempNHum(bot))
    
class TempNHum(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @commands.hybrid_command()
    async def check_temp(self, ctx : commands.Context):
        """Check the temperature inside the incubator"""
        await ctx.send("Please wait. Processing the temperature...")
        
        temp = await th.get_temperature()
        if temp == None:
            await ctx.send("Failed to measure temperature. Please try again later")
        else:
            embed = discord.Embed(title="Check Temperature", description=f'The current temperature inside the incubator is {temp}°C', color=11267612)
            embed.set_footer(text="Data taken at")
            embed.timestamp = discord.utils.utcnow()
            embed.set_image(url='https://i.pinimg.com/736x/85/5f/43/855f43700c855888a8f265185aacfbd9.jpg')
            
            await ctx.send(embed=embed)
        
        # # Call the get_temperature function from th_ctrl.py
        # try:
        #     temperature = await th.get_temperature()
            
        #     embed = discord.Embed(title="Check Temperature", description=f'The current temperature inside the incubator is {temperature}°C', color=11267612)
        #     embed.set_footer(text="Data taken at")
        #     embed.timestamp = discord.utils.utcnow()
        #     embed.set_image(url='https://i.pinimg.com/736x/85/5f/43/855f43700c855888a8f265185aacfbd9.jpg')
            
        #     await ctx.send(embed=embed)
        # except Exception as e:
        #     await ctx.send(f"Error: {str(e)}")
        
    @commands.hybrid_command()
    async def check_humidity(self, ctx : commands.Context):
        """Check the humidity inside the incubator"""
        await ctx.send("Please wait. Processing the humidity...")
        
        hum = await th.get_humidity()
        if hum == None:
            await ctx.send("Failed to measure humidity. Please try again later")
        else:
            embed = discord.Embed(title="Check Humidity", description=f'The current humidity inside the incubator is {hum}%', color=1891822)
            embed.set_footer(text="Data taken at")
            embed.timestamp = discord.utils.utcnow()
            embed.set_image(url='https://i.pinimg.com/736x/d1/da/0c/d1da0ca0ceb9057e0c7e720079190e19.jpg')
            
            await ctx.send(embed=embed)
        
        # Call the get_humidity function from th_ctrl.py
        # try:
        #     humidity = await th.get_humidity()
            
        #     embed = discord.Embed(title="Check Humidity", description=f'The current humidity inside the incubator is {humidity}%', color=1891822)
        #     embed.set_footer(text="Data taken at")
        #     embed.timestamp = discord.utils.utcnow()
        #     embed.set_image(url='https://i.pinimg.com/736x/d1/da/0c/d1da0ca0ceb9057e0c7e720079190e19.jpg')
            
        #     await ctx.send(embed=embed)
        # except Exception as e:
        #     await ctx.send(f"Error: {str(e)}")