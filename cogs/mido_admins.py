import discord
from discord.ext import commands

import traceback
import textwrap
import asyncio
import subprocess
import io
import psutil

from contextlib import redirect_stdout

class mido_admins(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot
        
        self.result = None
    
    #check func
    async def cog_check(self, ctx):
        return ctx.author.id in [m.id for m in ctx.bot.get_guild(701131006698192916).get_role(861832139204591626).members]
    
    #remove ```
    def cleanup_code(self, content):
        if content.startswith('```') and content.endswith('```'):
            return '\n'.join(content.split('\n')[1:-1])

        return content.strip('` \n')
    
    #create shell process
    async def run_process(self, command):
        try:
            process = await asyncio.create_subprocess_shell(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            result = await process.communicate()
        except NotImplementedError:
            process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            result = await self.bot.loop.run_in_executor(None, process.communicate)

        return [output.decode() for output in result]
    
    #eval
    @commands.command(pass_context=True)
    async def eval(self, ctx, *, body: str):
        env = {
            'bot': self.bot,
            'ctx': ctx,
            'self': self,
            '_': self.result
        }

        env.update(globals())

        body = self.cleanup_code(body)
        stdout = io.StringIO()

        to_compile = f'async def func():\n{textwrap.indent(body, "  ")}'

        try:
            exec(to_compile, env)
        except Exception as exc:
            return await ctx.send(f"```py\n{exc.__class__.__name__}: {exc}\n```")

        func = env['func']
        try:
            with redirect_stdout(stdout):
                ret = await func()
        except:
            value = stdout.getvalue()
            await ctx.send(f'```py\n{value}{traceback.format_exc()}\n```')
        else:
            value = stdout.getvalue()

            if ret is None:
                if value:
                    await ctx.send(f'```py\n{value}\n```')
            else:
                self.result = ret
                await ctx.send(f'```py\n{value}{ret}\n```')
    
    #sh
    @commands.command(pass_context=True, aliases=["sh"])
    async def shell(self, ctx, *, command):
        stdout, stderr = await self.run_process(command)
        
        if stderr:
            text = f"stdout: \n{stdout} \nstderr: \n{stderr}"
        else:
            text = f"{stdout}"

        try:
            ret = f"```\n{text}\n```"
            
            return await ctx.send(ret)   
        except Exception as exc:
            return await ctx.send(embed=f"```py\n{exc}\n```")
    
    #debug
    @commands.command()
    async def debug(self, ctx):
        e = discord.Embed(title="Debug Info", description="")
        
        cpu = psutil.cpu_percent()
        memory = psutil.virtual_memory()
        swap = psutil.swap_memory()
        disk = psutil.disk_usage("/")
        
        memory_used = (memory.used / 1024 / 1024 / 1024 * 200 + 1) // 2 / 100
        memory_total = (memory.total / 1024 / 1024 / 1024 * 200 + 1) // 2 / 100
        swap_used = (swap.used / 1024 / 1024 / 1024 * 200 + 1) // 2 / 100
        swap_total = (swap.total / 1024 / 1024 / 1024 * 200 + 1) // 2 / 100
        disk_used = (disk.used / 1024 / 1024 / 1024 * 200 + 1) // 2 / 100
        disk_total = (disk.total / 1024 / 1024 / 1024 * 200 + 1) // 2 / 100
        
        e.add_field(name="CPU Info", value=f"{cpu}%")
        e.add_field(name="Memory Info", value=f"Total: {memory_total}GB ({memory.percent}%), Used: {memory_used}GB, Free: {round(memory_total - memory_used)}GB", inline=False)
        e.add_field(name="Swap Memory Info", value=f"Total: {swap_total}GB ({swap.percent}%), Used: {swap_used}GB, Free: {swap_total - swap_used}GB", inline=False)
        e.add_field(name="Disk Info", value=f"Total: {disk_total}GB ({disk.percent}%), Used: {disk_used}GB, Free: {round(disk_total - disk_used)}GB", inline=False)
        await ctx.send(embed=e)
        
def setup(bot):
    bot.add_cog(mido_admins(bot))
