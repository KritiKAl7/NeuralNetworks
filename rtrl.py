#RTRL Learning by Zhepei Wang
import numpy as np
import copy

# the activation function is borrowed from Prof. Keller's backprop.py
class ActivationFunction:
    """ ActivationFunction packages a function together with its derivative. """
    """ This prevents getting the wrong derivative for a given function.     """
    """ Because some derivatives are computable from the function's value,   """
    """ the derivative has two arguments: one for the argument and one for   """
    """ the value of the corresponding function. Typically only one is use.  """

    def __init__(af, name, fun, deriv):
        af.name = name
        af.fun = fun
        af.deriv = deriv

    def fun(af, x):
        return af.fun(x)

    def deriv(af, x, y):
        return af.deriv(x, y)
logsig = ActivationFunction("logsig",
                            lambda x: 1.0/(1.0 + np.exp(-x)),
                            lambda x,y: y - y * y)

tansig = ActivationFunction("tansig",
                            lambda x: np.tanh(x),
                            lambda x,y: 1.0 - y*y)

purelin = ActivationFunction("purelin",
                             lambda x: x,
                             lambda x,y: 1)

def parseIO(X):
    X = np.matrix(X).transpose()
    return X

def initW(row, col):
    return np.matrix(np.random.rand(row, col))

def genBeats(pattern, numSlots):
    numTrack = len(pattern)
    X = [0 for beat in range(numSlots)]
    y = [[0 for x in range(2 ** numTrack)] for beat in range(numSlots)]
    for beat in range(numSlots):
        beatIndex = 0
        for trackIndex in range(numTrack):
            track = pattern[trackIndex]
            if beat in track:
                beatIndex += 2 ** trackIndex
        y[beat][beatIndex] = 1
    X[0] = 1
    return X, y

# global config
X = []
y = []
inputDim, numSample, outputDim, hiddenDim = 0, 0, 0, 0
W = []


def forwardFeed(W, Z, t, neuronType):
    # Z supposed to be updated
    Z[inputDim:, t] = neuronType.fun(W * Z[:, t - 1])
    return Z[inputDim: , t]

def train(X, y, neuronType, rate=1.0, max_iter=25000, threshold=0.05, \
    displayInterval=100, noisy=False):
    epoch = 0
    global W
    for epoch in range(max_iter):
        H = np.matrix([[0. for col in range(numSample + 1)] for row in range(hiddenDim)])
        Z = np.vstack((X, H))
        MSE = 0
        pTL = [[[[0. for col in range(inputDim + hiddenDim)] \
        for row in range(hiddenDim)] \
        for k in range(hiddenDim)] for t in range(numSample + 1)]
        
        for t in range(1, numSample + 1):
            pred = forwardFeed(W, Z, t, neuronType)
            e = y[:, t - 1] - pred
            MSE += 0.5 * ((e.transpose() * e)).item(0)  
            # calculate p and gradW for sample T
            for i in range(hiddenDim):
                for j in range(inputDim + hiddenDim):
                    accumK = 0
                    for k in range(hiddenDim):
                        accumL = 0
                        for l in range(hiddenDim):
                            accumL += W.item(k, inputDim + l) * pTL[t - 1][l][i][j]
                        if i == k:
                            accumL += Z.item(j, t - 1)
                        pTL[t][k][i][j] = neuronType.deriv(None, Z.item(inputDim + k, t)) * accumL
                        accumK += e.item(k) * pTL[t][k][i][j]
                    W[i, j] += rate * accumK
        MSE /= numSample
        if MSE <= threshold:
            print "Epoch {}, Final MSE: {}".format(epoch, MSE)
            return W
        if epoch % displayInterval == 0:
            print "MSE for epoch {}: {}".format(epoch, MSE)

    print "Epoch {}, Final Squared MSE: {}".format(epoch, MSE)
    return W

def assess(W, X, y, neuronType):
    H = np.matrix([[0. for col in range(numSample + 1)] for row in range(hiddenDim)])
    Z = np.vstack((X, H))
    print '---------testing----------'
    for t in range(1, numSample + 1):
        Z[inputDim:, t] = neuronType.fun(W * Z[:, t - 1])
        print "predicted: {}; expected: {}".format(np.argmax(Z[inputDim:, t]), np.argmax(y[:, t - 1]))
    return Z[inputDim:, -1]

def drumMachine(pattern, numSlots, runLength=25000, rate=0.5, neuronType=logsig):
    global X, y, inputDim, numSample, outputDim, hiddenDim, W
    # parsing data and setting config
    X, y = genBeats(pattern, numSlots)
    X = parseIO(X).transpose()
    y = parseIO(y)
    inputDim = X.shape[0]
    numSample = numSlots
    outputDim = y.shape[0]
    hiddenDim = outputDim
    X = np.hstack((X, np.matrix([[0] for i in range(inputDim)])))
    W = initW(hiddenDim, inputDim + hiddenDim)
    # print W.shape
    Wopt = train(X, y, neuronType, rate=rate, max_iter=runLength)
    assess(Wopt, X, y, neuronType)

pattern = [[0,4],[2,5,6], [0, 2, 4, 6]]
def main():
    drumMachine(pattern, 8, runLength=10000, rate=1.0)

main()
