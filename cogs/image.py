import discord
from discord.ext import commands
from discord import app_commands
from discord import File, Embed
from io import BytesIO
import contrls.img_ctrl as img

TEMP_FILE = "temp.jpg"

async def setup(bot: commands.Bot) :
    await bot.add_cog(ImageDisplay(bot))
    
class ImageDisplay(commands.Cog) :
    def __init__(self, bot) :
        self.bot = bot
        
    @commands.hybrid_command()
    async def take_photo(self, ctx : commands.Context):
        """Get the image from database"""
        # Call the get image function from img_ctrl.py
        await ctx.send("Please wait. Processing the image...")
        
        image = await img.get_image()
        if image == None:
            await ctx.send("Failed to retreive the image. Please try again later")
        else:
            buffer = BytesIO(image)
            buffer.seek(0)
            file = File(buffer, filename="photo.jpg")
            embed = embed = discord.Embed(title="Photo taken from inside the incubator", color=174301)
            embed.set_image(url="attachment://photo.jpg")
            
            await ctx.send(file=file, embed=embed)
            
        # image_bytes = await img.get_image()
        
        # if image_bytes:
        #     buffer = BytesIO(image_bytes)
        #     buffer.seek(0)
        #     file = File(buffer, filename="image.jpg")
            
        #     embed = embed = discord.Embed(title="Photo taken from inside the incubator", color=174301)
        #     embed.set_image(url="attachment://image.jpg")
            
        #     await ctx.send(file=file, embed=embed)
        # else:
        #     await ctx.send("Failed to retrieve the image. Please try again later.")
        
        # try:
        #     image = await img.get_image()

        #     if image == None:
        #         # raise execption if image is null
        #         raise Exception(f'No image found')
        #     elif not image:
        #         # raise execption if image is empty
        #         raise Exception(f'Image is empty')

        #     with open(TEMP_FILE, "wb") as f:
        #         f.write(image)
                
        #     embed = discord.Embed(title="Photo taken from inside the incubator", color=174301)
        #     embed.set_footer(text="Taken At")
        #     embed.timestamp = discord.utils.utcnow()
        
        #     await ctx.send(file=discord.File(TEMP_FILE), embed=embed)
        # except Exception as e:
        #     await ctx.send(f"Error: {str(e)}")