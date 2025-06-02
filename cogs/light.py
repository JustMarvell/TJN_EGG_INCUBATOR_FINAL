import discord
from discord.ext import commands
from discord import app_commands
import contrls.lgh_ctrl as lgh

async def setup(bot: commands.Bot):
    await bot.add_cog(LightControl(bot))
    
class LightControl(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @commands.hybrid_command()
    async def toggle_light(self, ctx: commands.Context, action: str = None):
        """Toggle the light based on input"""
        await ctx.send("Please wait. Processing the light toggle...")
        
        if action is None or action.lower() == "status":
            state = await lgh.toggle_light("status")
            if state == None:
                await ctx.send("Error: Unable to retrieve the current state of the light.")
            else:
                await self.send_embed(ctx, "Toggle Light : Status", f"Current light status: {state}", 'https://i.pinimg.com/736x/55/1f/bd/551fbd3933bf0240e49d6cdf45e1ae02.jpg', 15466240)
        elif action.lower() == 'on' or action.lower() == 'off':
            lamp = await lgh.toggle_light(action.lower())
            if lamp is None:
                await ctx.send(f"Error: Unable to turn {action.lower()} the light.")
            else:
                if lamp == True:
                    state = "On"
                    img = 'https://i.pinimg.com/736x/55/1f/bd/551fbd3933bf0240e49d6cdf45e1ae02.jpg'
                    color = 15466240
                else:
                    state = "Off"
                    img = 'https://i.pinimg.com/736x/83/e6/e9/83e6e9bcb32c8a70cf6e01b37f3004e1.jpg'
                    color = 789516
                
                await self.send_embed(ctx, f"Toggle Light : {lamp}", f"Light has been turned {state}", img, color)
        else:
            await ctx.send("Invalid command ['on' | 'off' | 'status']")
        # Call the toggle_light function from lgh_ctrl.py
        # try:
        #     if action is None or action.lower() == "status":
        #         # Get the current state of the light
        #         current_state = await lgh.toggle_light("status")
                
        #         if current_state == None:
        #             await ctx.send("Error: Unable to retrieve the current state of the light.")
        #         elif current_state == "ON":
        #             await self.send_embed(ctx, "Toggle Light : Status", "Current light status: ON", 'https://i.pinimg.com/736x/55/1f/bd/551fbd3933bf0240e49d6cdf45e1ae02.jpg', 15466240)
        #         elif current_state == "OFF":
        #             await self.send_embed(ctx, "Toggle Light : Status", "Current light status: OFF", 'https://i.pinimg.com/736x/83/e6/e9/83e6e9bcb32c8a70cf6e01b37f3004e1.jpg', 789516)
                
        #     elif action.lower() == "on":
        #         respon = await lgh.toggle_light("on")
        #         # https://i.pinimg.com/736x/55/1f/bd/551fbd3933bf0240e49d6cdf45e1ae02.jpg
        #         if respon == None:
        #             await ctx.send("Error: Unable to turn on the light.")
        #         else:
        #             await self.send_embed(ctx, "Toggle Light : ON", "Light has been turned ON", 'https://i.pinimg.com/736x/55/1f/bd/551fbd3933bf0240e49d6cdf45e1ae02.jpg', 15466240)
        #     elif action.lower() == "off":
        #         respon = await lgh.toggle_light("off")
        #         # https://i.pinimg.com/736x/83/e6/e9/83e6e9bcb32c8a70cf6e01b37f3004e1.jpg
        #         if respon == None:
        #             await ctx.send("Error: Unable to turn off the light.")
        #         else:
        #             await self.send_embed(ctx, "Toggle Light : OFF", "Light has been turned OFF", 'https://i.pinimg.com/736x/83/e6/e9/83e6e9bcb32c8a70cf6e01b37f3004e1.jpg', 789516)
        #     else:
        #         await ctx.send("Invalid action. Use 'on', 'off', or leave it blank to check the current state.")
        # except Exception as e:
        #     await ctx.send(f"Error: {str(e)}")
            
    async def send_embed(self, ctx, title, description, image_url, color):
        embed = discord.Embed(title=title, description=description, color=color)
        
        embed.add_field(name="/toggle_light on", value="To switch on the light", inline=False)
        embed.add_field(name="/toggle_light off", value="To switch off the light", inline=False)
        
        embed.set_image(url=image_url)
        await ctx.send(embed=embed)