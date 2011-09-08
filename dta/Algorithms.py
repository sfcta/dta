__copyright__   = "Copyright 2011 SFCTA"
__license__     = """
    This file is part of DTA.

    DTA is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    DTA is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with DTA.  If not, see <http://www.gnu.org/licenses/>.
"""

def dfs(net, root=None):
    """
    Non-Recursive depth first search algorithm with 
    pre and post orderings. At the end of the execution
    all nodes in the network have a pre and post numbers
    and predecessor nodes assigned to them.
    """
    
    time = 0
    for node in net.iterNodes():
        node.pre = 0
        node.post = 0
        node.pred = None
        node.visited = False 

    allNodes = [node for node in net.iterNodes()]
    if root:
        allNodes.remove(root)
        allNodes.insert(0, root)

    nodesToExamine = []

    for node in allNodes:
        
        if node.pre == 0:
            nodesToExamine.append(node)

        while nodesToExamine:        
            pivot = nodesToExamine[-1]
            if pivot.visited == False:            
                for downNode in pivot.iterDownstreamNodes():                
                    if downNode.visited == False:                    
                        nodesToExamine.append(downNode)
                        downNode.pred = pivot 
                pivot.visited = True
                time += 1
                pivot.pre = time 
            elif pivot.post > 0:
                nodesToExamine.pop() 
            else:
                time += 1
                pivot.post = time

def getMetaGraph(net):
    """
    Return a network that represents the meta graph of the input network. 
    At the end of the execution of this algorithm each node points to 
    its metanode
    """
    pass 


def hasPath(net, originNode, destNode):
    """
    Return true if the network has a path 
    from the origin node to the destination node
    """
    
    dfs(net, originNode) 

    node = destNode
    while node and node != originNode:
        node = node.pred 

    if node is None:
        return False
    return True
    


                    
        
        
        
        

