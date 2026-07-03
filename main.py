from context import Context
#import os
import sys

def main():
    
    if len(sys.argv) < 2:
        print("Missing arguments !!")
        return None

    print(sys.argv[1])
    configFile = sys.argv[1]
    context = Context()
    context.loadConfiguration(configFile)

if __name__ == '__main__':
  main()