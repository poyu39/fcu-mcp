import json

import dotenv
from fastmcp import FastMCP

from .api import ILearnAPI, MyFcuAPI
from .driver import UserDriverManager
from .logger import logger

driver_manager = UserDriverManager()

mcp = FastMCP(
    name='fcu',
)

@mcp.tool()
def login(username: str, password: str) -> str:
    try:
        ilearn_is_logged_in = driver_manager.is_ilearn_logged_in(username)
        myfcu_is_logged_in = driver_manager.is_myfcu_logged_in(username)
        
        if ilearn_is_logged_in and myfcu_is_logged_in:
            logger.info(f'User {username} is already logged in to both iLearn and MyFCU')
            return json.dumps({
                'status': 'success',
                'message': f'User {username} is already logged in to both iLearn and MyFCU'
            })
        
        if not ilearn_is_logged_in:
            logger.info(f'User {username} is not logged in to iLearn, logging in now')
            
            driver = driver_manager.get_driver(username)
            api = ILearnAPI(driver)
            if not api.login(username, password):
                raise Exception('Invalid iLearn username or password')
            
            ilearn_is_logged_in = True
            logger.info(f'User {username} logged in to iLearn successfully')
        
        if not myfcu_is_logged_in:
            logger.info(f'User {username} is not logged in to MyFCU, logging in now')
            
            driver = driver_manager.get_driver(username)
            api = MyFcuAPI(driver)
            if not api.login(username, password):
                raise Exception('Invalid MyFCU username or password')
            
            myfcu_is_logged_in = True
            logger.info(f'User {username} logged in to MyFCU successfully')
        
        if ilearn_is_logged_in and myfcu_is_logged_in:
            return json.dumps({
                'status': 'success',
                'message': f'User {username} logged in to both iLearn and MyFCU successfully'
            })
        
    except Exception as e:
        logger.error(f'Login failed for user {username}: {str(e)}')
        return json.dumps({
            'status': 'error',
            'message': str(e)
        })

@mcp.tool()
def get_future_events(username: str) -> str:
    try:
        if not driver_manager.is_ilearn_logged_in(username):
            raise Exception('User iLearn is not logged in')
        
        driver = driver_manager.get_driver(username)
        api = ILearnAPI(driver)
        
        events = api.get_future_events()
        logger.info(f'Fetched future events for user {username}')
        
        return json.dumps({
            'status': 'success',
            'events': events
        })
    
    except Exception as e:
        logger.error(f'Failed to get future events for user {username}: {str(e)}')
        return json.dumps({
            'status': 'error',
            'message': str(e)
        })

@mcp.tool()
def get_course_list(username: str, year: int, semester: int) -> str:
    try:
        if not driver_manager.is_myfcu_logged_in(username):
            raise Exception('User MyFCU is not logged in')
        
        driver = driver_manager.get_driver(username)
        api = MyFcuAPI(driver)
        
        courses = api.get_course_list(year, semester)
        logger.info(f'Fetched course list for user {username}')
        
        return json.dumps({
            'status': 'success',
            'courses': courses
        })
    
    except Exception as e:
        logger.error(f'Failed to get course list for user {username}: {str(e)}')
        return json.dumps({
            'status': 'error',
            'message': str(e)
        })


def main():
    logger.info('start iLearn server')
    port = dotenv.get_key('.env', 'PORT')
    mcp.run(transport='streamable-http', port=int(port))
