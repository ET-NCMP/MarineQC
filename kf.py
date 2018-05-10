import numpy as np
#import matplotlib.pyplot as plt
import random

class KalmanFilter:

    def __init__(self, delta_t):
    
        self.make_F(delta_t)
        self.make_G(delta_t)
        
        self.H = np.matrix([
                           [1.0, 0.0, 0.0, 0.0],
                           [0.0, 0.0, 1.0, 0.0]
                          ])

        self.I = np.matrix([
                           [1.0, 0.0, 0.0, 0.0],
                           [0.0, 1.0, 0.0, 0.0],
                           [0.0, 0.0, 1.0, 0.0],
                           [0.0, 0.0, 0.0, 1.0]
                          ])

    def make_F(self, delta_t):
    
        self.F = np.matrix([
                           [1.0, delta_t,  0.0,     0.0],
                           [0.0,     1.0,  0.0,     0.0],              
                           [0.0,     0.0,  1.0, delta_t],              
                           [0.0,     0.0,  0.0,     1.0]
                          ])
  
    def make_G(self, delta_t):
        self.G = np.matrix([
                           [(delta_t**2.)/2.,           0.0],
                           [delta_t,                    0.0],
                           [0.0,           (delta_t**2.)/2.],
                           [0.0,                    delta_t]
                          ])
    
    def set_initial_state(self,x,P):
    
        self.xkm1 = x
        self.P = P
    
    def predict(self, Q, delta_t):
    
        self.make_F(delta_t)
        self.make_G(delta_t)
        
        Pkkm1 = self.F * self.P * self.F.T  + self.G * Q * self.G.T
        xkkm1 = self.F * self.xkm1
    
        return Pkkm1,xkkm1
    
    def update(self, z, R, Q, delta_t):

        self.make_F(delta_t)
        self.make_G(delta_t)
    
        Pkkm1, xkkm1 = self.predict(Q, delta_t)

        bracket = self.H * Pkkm1 * self.H.T + R
        W = Pkkm1 * self.H.T * bracket.I
        xkk = xkkm1 + W * (z - self.H * xkkm1)
        Iminus = (self.I - W * self.H)
        Pkk = Iminus * Pkkm1 * Iminus.T + W * R * W.T

        self.xkm1 = xkk
        self.P = Pkk
        
    def get_state(self):
        return self.xkm1
        
    @staticmethod
    def make_R(sigma_x, sigma_y):
        
        R = np.matrix([
                      [sigma_x**2,         0.0],
                      [0.0,         sigma_y**2]
                     ])
    
        return R
        

'''
delta_t = 2.0
sigma_x = 0.2
sigma_y = 0.2
sigma_v = 0.1

xkm1 = np.matrix([[20.0],[0.0],[0.0],[0.0]])

R = KalmanFilter.make_R(sigma_x, sigma_y)
Q = KalmanFilter.make_R(sigma_v, sigma_v)

P = np.matrix([
              [10.0,  0.0,   0.0,   0.0],
              [0.0,  10.0,   0.0,   0.0],
              [0.0,   0.0,  10.0,   0.0],
              [0.0,   0.0,   0.0,  10.0]
             ])

k = KalmanFilter(delta_t)
k.set_initial_state(xkm1,P)

xs = []
ys = []
txs = []
tys = []
pxs = []
pys = []
pys_up = []
pys_do = []

for i in range(0,100):
    
    noisex = random.gauss(0,sigma_x)
    noisey = random.gauss(0,sigma_y)
    
    trux = 3.5 + float(i)*0.001 + 10. * np.cos(float(i)/20.)
    truy = 0.1 + float(i)*0.002 + 13. * np.sin(float(i)/15.)
   
    if i == 50:
        truy = truy + 1.0
        trux = trux - 2.0
   
    xxx = noisex + trux
    yyy = noisey + truy
   
    z = np.matrix([
                  [xxx],
                  [yyy]
                  ])

    P_pred, x_pred = k.predict(Q, delta_t)
                  
    k.update(z,R,Q, delta_t)
    s = k.get_state()
    
    mu = np.matrix([[x_pred[0,0]],[x_pred[2,0]]])
    big_sig = np.matrix([
                        [P_pred[0,0],P_pred[0,2]],
                        [P_pred[2,0],P_pred[2,2]]
                       ])
    
    big_sig = big_sig + R    
    
    det = big_sig[0,0]*big_sig[1,1] - big_sig[0,1]*big_sig[1,0]
    
    xminmu = z-mu
    gh = xminmu.T * big_sig.I * xminmu
    prob = (1./np.sqrt(4.*np.pi*np.pi*det))*np.exp(-0.5*gh[0,0])
    
    p_data_given_good = prob * 0.1 * 0.1
    p_data_given_g = 1./(400.*400.)
    p_g = 0.02
    
    p_gross_given_data = (p_data_given_g * p_g /
                          (p_data_given_g * p_g + 
                           p_data_given_good * (1.0 - p_g)))
    
    print i,s[0][0],xxx,p_gross_given_data
    txs.append(trux)
    tys.append(truy)
    xs.append( z[0,0])
    ys.append( z[1,0])
    pxs.append(x_pred[0,0])
    pys.append(x_pred[2,0])
    pys_up.append(np.sqrt(P_pred[0,0]))
    pys_do.append(np.sqrt(P_pred[2,2]))
             
plt.plot(xs,ys)
plt.plot(txs,tys,color="Red")
plt.plot(pxs,pys,color="Black")

for i in range(0,100):
    plt.plot([pxs[i]-2*pys_up[i],pxs[i]+2*pys_up[i],pxs[i]+2*pys_up[i],pxs[i]-2*pys_up[i],pxs[i]-2*pys_up[i]],
             [pys[i]-2*pys_do[i],pys[i]-2*pys_do[i],pys[i]+2*pys_do[i],pys[i]+2*pys_do[i],pys[i]-2*pys_do[i]],
             color="Grey")

#plt.plot(pxs,pys_up,color="Black")
#plt.plot(pxs,pys_do,color="Black")
plt.show()
             
pass
'''