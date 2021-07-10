import discord
from discord.ext import commands

import traceback
import textwrap
import asyncio
import subprocess
import io
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
        except Exception as e:
            return await ctx.send(f"```py\n{e.__class__.__name__}: {e}\n```")

        func = env['func']
        try:
            with redirect_stdout(stdout):
                ret = await func()
        except Exception as e:
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
        except Exception as er:
            return await ctx.send(embed=f"```py\n{er}\n```")
    
def setup(bot):
    bot.add_cog(mido_admins(bot))
