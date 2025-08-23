"""Main application module for Savanty."""

import os
import sys
from typing import Optional
import click
from fastapi import FastAPI, Form, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import uvicorn
from savanty.solver import solve_optimization_problem, ProblemSolverResult

try:
    from fastmcp import FastMCP
    FASTMCP_AVAILABLE = True
except ImportError:
    FASTMCP_AVAILABLE = False


class SolveRequest(BaseModel):
    problem_description: str
    additional_info: str = ""


def create_app():
    """Create and configure the FastAPI application."""
    app = FastAPI(title="Savanty API", version="0.2.0")

    @app.get("/", response_class=HTMLResponse)
    async def index():
        """Render the main dashboard page."""
        return """
        <html>
            <head>
                <title>Savanty - Optimization Problem Solver</title>
            </head>
            <body>
                <h1>Savanty - Optimization Problem Solver</h1>
                <form action="/solve" method="post">
                    <label for="problem_description">Problem Description:</label><br>
                    <textarea id="problem_description" name="problem_description" rows="4" cols="50"></textarea><br>
                    <label for="additional_info">Additional Information (optional):</label><br>
                    <textarea id="additional_info" name="additional_info" rows="2" cols="50"></textarea><br>
                    <input type="submit" value="Solve">
                </form>
            </body>
        </html>
        """

    @app.post("/solve")
    async def solve(request: SolveRequest):
        """Solve an optimization problem."""
        try:
            result = solve_optimization_problem(
                request.problem_description, request.additional_info
            )

            if result.needs_more_info:
                return {
                    "needs_more_info": True,
                    "questions": result.questions,
                    "log": "Please provide more information to solve this problem."
                }
            elif result.error:
                raise HTTPException(status_code=400, detail={
                    "error": result.error,
                    "log": f"Error occurred while solving: {result.error}"
                })
            else:
                return {
                    "solution": result.solution,
                    "log": "Problem solved successfully."
                }
        except Exception as e:
            raise HTTPException(status_code=400, detail={
                "error": str(e),
                "log": f"Error occurred while solving: {str(e)}"
            })

    return app


@click.command()
@click.option('--problem', '-p', help='Optimization problem description')
@click.option('--web', '-w', is_flag=True, help='Run web interface')
@click.option('--mcp', '-m', is_flag=True, help='Run as Model Context Protocol server')
@click.option('--port', default=int(os.getenv('SAVANTY_PORT', 8000)), help='Port for web interface')
def main(problem: Optional[str], web: bool, mcp: bool, port: int):
    """Savanty CLI - An intelligent optimization problem solver.
    
    Examples:
      savanty -p "Minimize x+y subject to x>=0, y>=0, x+y<=10"
      savanty --web
      savanty --mcp
    """
    if mcp:
        # Run as MCP server
        if not FASTMCP_AVAILABLE:
            print("Error: fastmcp package not installed. Please run 'pip install fastmcp'")
            sys.exit(1)
            
        # Create FastMCP app
            mcp_app = FastMCP("Savanty Optimizer")
        
        @mcp_app.prompt(name="solve_optimization")
        async def solve_optimization(problem: str) -> str:
            """Solve an optimization problem using Savant.
            
            Args:
                problem: The optimization problem description
                
            Returns:
                The solution to the optimization problem
            """
            try:
                result = solve_optimization_problem(problem, "")
                if result.error:
                    return f"Error: {result.error}"
                return f"Solution: {result.solution}"
            except Exception as e:
                return f"Error occurred: {str(e)}"
        
        print("Starting Savanty MCP server on stdin/stdout...")
        mcp_app.run()
    elif web:
        # Run web interface
        app = create_app()
        uvicorn.run(app, host="0.0.0.0", port=port)
    elif problem:
        # Solve problem from command line
        current_problem = problem
        additional_info = ""
        
        while True:
            result = solve_optimization_problem(current_problem, additional_info)
            
            if result.needs_more_info:
                click.echo("I need more information to solve this problem:")
                for i, question in enumerate(result.questions, 1):
                    click.echo(f"{i}. {question}")
                
                # Ask user for additional information
                user_input = click.prompt("Please provide the missing information", type=str)
                additional_info = user_input
                # We'll try again with the additional info
                continue
            elif result.error:
                click.echo(f"Error: {result.error}", err=True)
                sys.exit(1)
            else:
                click.echo("Solution found:")
                click.echo(result.solution)
                break
    else:
        # Show help if no options provided
        click.echo("Savanty: An intelligent optimization problem solver")
        click.echo("Use --help for more information")


if __name__ == '__main__':
    main()