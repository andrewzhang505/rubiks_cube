import matplotlib.pyplot as plt
import math
from mpl_toolkits import mplot3d
import numpy as np
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import random as rand

class quaternion():
    """Generic quaternion class
    
    """
    def __init__(self,c,x,y,z):
        """Create quaternion
        
        Arguments:
            (c,x,y,z) = c + xi + yj + zk
        """
        self.c=c
        self.x=x
        self.y=y
        self.z=z
    
    def get_coord(self):
        """Obtain coordinates
        
        Returns:
            (float, float, float, float) -- coordinates
        """
        return (self.c, self.x, self.y, self.z)

    def multiply(quat1, quat2):
        """Multiply 2 quaternions. Note, order matters
        
        Arguments:
            quat1 {quaternion}
            quat2 {quaternion}
        
        Returns:
            quaternion - product of quat1*quat2
        """
        (c1,x1,y1,z1)=quat1.get_coord()
        (c2,x2,y2,z2)=quat2.get_coord()
        
        c3=c1*c2-x1*x2-y1*y2-z1*z2
        x3=c1*x2+x1*c2+y1*z2-z1*y2
        y3=c1*y2-x1*z2+y1*c2+z1*x2
        z3=c1*z2+x1*y2-y1*x2+z1*c2
        
        return quaternion(c3,x3,y3,z3)
    
    def conjugate(quat):
        """Returns conjugate (c - xi - yj - zk) of input
        
        Arguments:
            quat {quaternion}
        
        Returns:
            quaternion
        """
        (c,x,y,z)=quat.get_coord()
        return quaternion(c,-x,-y,-z)

class face():
    def __init__(self, color, x,y,z, direction, size):
        self.color=color
        self.quat=quaternion(0,x,y,z)
        self.direction=quaternion(0,*direction)
        self.size=size
    
    def rotate(self, angle, x,y,z):
        s=math.sin(angle/2)
        r=quaternion(math.cos(angle/2), s*x, s*y, s*z)
        q1 = quaternion.multiply(r, self.quat)
        self.quat = quaternion.multiply(q1, quaternion.conjugate(r))
        
        q2 = quaternion.multiply(r, self.direction)
        self.direction = quaternion.multiply(q2, quaternion.conjugate(r))
    
    def draw(self, ax):
        (_,x,y,z)=self.quat.get_coord()
        (_,d1,d2,d3)=self.direction.get_coord()
        
        dim1=[-self.size, self.size, self.size, -self.size]
        dim2=[-self.size, -self.size, self.size, self.size]
        
        x_list=[x]*4
        y_list=[y]*4
        z_list=[z]*4
        
        idx = np.argmax([abs(d1), abs(d2), abs(d3)])
        
        if idx==0:
            y_list = [y_list[i]+dim1[i] for i in range(4)]
            z_list = [z_list[i]+dim2[i] for i in range(4)]
        elif idx==1:
            x_list = [x_list[i]+dim1[i] for i in range(4)]
            z_list = [z_list[i]+dim2[i] for i in range(4)]
        else:
            y_list = [y_list[i]+dim1[i] for i in range(4)]
            x_list = [x_list[i]+dim2[i] for i in range(4)]
        
        verts = [list(zip(x_list,y_list,z_list))]
        ax.add_collection3d(Poly3DCollection(verts, 
             facecolors=self.color, linewidths=1, edgecolors='k', alpha=1))

class rubiks_cube():
    colors={'white':(1,0,0), 'red':(0,1,0), 'blue':(0,0,1), 'yellow':(-1,0,0), 'orange':(0,-1,0), 'green':(0,0,-1)}
        
    def __init__(self):
        self.faces=[]
        self.fig = plt.figure()
        self.ax = plt.axes(projection='3d')
        
        for c in self.colors:
            for i in [-2/3,0,2/3]:
                for j in [-2/3,0,2/3]:
                    (x,y,z)=self.colors[c]
                    if x != 0:
                        y=i
                        z=j
                    elif y != 0:
                        z=i
                        x=j
                    else:
                        x=i
                        y=j
                    self.faces.append(face(c,x,y,z,direction=self.colors[c], size=1/3))
    
    def draw(self):
        plt.cla()
        for f in self.faces:
            f.draw(self.ax)
        self.ax.set_xlim(-1.5,1.5)
        self.ax.set_ylim(-1.5,1.5)
        self.ax.set_zlim(-1.5,1.5)
        self.fig.canvas.draw()
        
    
    def turn_side(self, color, angle):
        vec = self.colors[color]
        for f in self.faces:
            q = f.quat
            v = (q.x*vec[0], q.y*vec[1], q.z*vec[2])
            if sum(v)>0.5:
                f.rotate(angle, *vec)
    
    def scramble(self, moves=20, draw=True):
        for i in range(moves):
            c = rand.choice(list(self.colors.keys()))
            angle = rand.choice([math.pi/2, -math.pi/2])
            self.turn_side(c,angle)
            if draw:
                self.draw()
    
    def is_solved(self):
        for f in self.faces:
            ans = [0]+[round(i) for i in self.colors[f.color]]
            d = [round(i) for i in f.direction.get_coord()]
            if ans!=d:
                return False
        return True
    
        

if __name__=='__main__':
    rand.seed()
    plt.ion()
    r = rubiks_cube()
    r.draw()
    colors = {'w':'white', 'r':'red', 'b':'blue', 'y':'yellow', 'o':'orange', 'g':'green'}
    directions = {'+':math.pi/2, '-':-math.pi/2}
    while(True):
        i = input("Input command:")
        try:
            if i=='break':
                break
            elif i=='help':
                print("break: exit program")
                print("sXX: scramble cube (XX is the number of moves to scramble)")
                print("?: check if cube is solved")
                print("CD: rotate side. C-color{r,g,b,w,y,o}, D-direction{+,-}")
            elif i=="?":
                print(r.is_solved())
            elif 's' in i:
                if len(i)>1:
                    num=int(i[1:])
                else:
                    num=20
                r.scramble(num)
                r.draw()
            else:
                c = colors[i[0]]
                d = directions[i[1]]
                r.turn_side(c,d)
                r.draw()
        except:
            print('Invalid input. Type "help" for details')