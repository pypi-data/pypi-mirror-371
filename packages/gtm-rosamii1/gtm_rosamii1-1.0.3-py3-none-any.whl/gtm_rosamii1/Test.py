import asyncio
import gtm_agent

async def main():
    await (gtm_agent.start(""))

if __name__ == "__main__":
    asyncio.run(main())