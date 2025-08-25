from quacknet.core.optimisers import Adam
from quacknet.core.losses.lossFunctions import MSELossFunction

class Transformer:
    def __init__(self):
        """
        Initializes the model with an Adam optimizer instance and
        an empty dictionary to store model blocks.        
        """
        self.adam = Adam(self.forwardPropagation, self.backwardPropagation)
        
        self.blocks = {}

    def addBlock(self, block):
        """
        Adds a new block/module to the model's blocks dictionary.

        Args:
            block (object): A model block or layer to be added.
        """
        self.blocks.update({len(self.blocks): block})
    
    def forwardPropagation(self, input):
        for key in self.blocks:
            if(key == 0):
                input = self.blocks[key].forwardPropagation(input)
            else:
                input = self.blocks[key].forwardPropagation(input, False)
        return input

    def backwardPropagation(self, output, labels):
        Parameters = {}
        Gradients = {}
        for blockKey in self.blocks:
            Param, Grad = self.blocks[blockKey].backwardPropagation(output, labels)

            for key in Param:
                Parameters.update({f"{blockKey}.{key}": Param[key]}) # block key: 2, key: ATT_WO
                Gradients.update({f"{blockKey}.{key}": Grad[key]})   # will become 2.ATT_WO
        
        return Parameters, Gradients

    def optimiser(self, inputData, labels, useBatches, batchSize, alpha, beta1, beta2, epsilon):
        AllOutputs, Parameters = self.adam.optimiser(inputData, labels, useBatches, batchSize, alpha, beta1, beta2, epsilon)       
        # Parameters will be like [b1.w1, b1.w2 ... b2.w1, b2.w2 ... bn.w1, b2.w2]
        for i in range(len(self.blocks)):
            self.blocks[i].norm1.gamma = Parameters[f"{i}.Norm1_gamma"]
            self.blocks[i].norm1.beta = Parameters[f"{i}.Norm1_beta"] 
            self.blocks[i].norm2.gamma = Parameters[f"{i}.Norm2_gamma"] 
            self.blocks[i].norm2.beta = Parameters[f"{i}.Norm2_beta"]
            self.blocks[i].FFN.W1 = Parameters[f"{i}.FFN_W1"] 
            self.blocks[i].FFN.b1 = Parameters[f"{i}.FFN_b1"] 
            self.blocks[i].FFN.W2 = Parameters[f"{i}.FFN_W2"] 
            self.blocks[i].FFN.b2 = Parameters[f"{i}.FFN_b2"] 
            self.blocks[i].attention.outputWeight = Parameters[f"{i}.ATT_WO"] 
            self.blocks[i].attention.outputBias = Parameters[f"{i}.ATT_BO"] 
            self.blocks[i].attention.QueryWeights = Parameters[f"{i}.ATT_WQ"] 
            self.blocks[i].attention.KeyWeights = Parameters[f"{i}.ATT_WK"] 
            self.blocks[i].attention.ValueWeights = Parameters[f"{i}.ATT_WV"]
            if(i == 0):
                self.blocks[i].embedding.weights = Parameters[f"{i}.Embed_W"]

        return AllOutputs, Parameters

    def train(self, inputData, labels, useBatches = False, batchSize = 16, alpha = 0.001, beta1 = 0.9, beta2 = 0.999, epsilon = 1e-8):
        """
        Trains the model on the input data and labels using the Adam optimizer,
        optionally with batching, and returns the mean squared error loss.

        Args:
            inputData (ndarray): Input data for training.
            labels (ndarray): True labels corresponding to the input data.
            useBatches (bool, optional): Whether to use mini-batching. Default is False.
            batchSize (int, optional): Size of each batch if batching is used. Default is 16.
            alpha (float, optional): Learning rate for the Adam optimizer. Default is 0.001.
            beta1 (float, optional): Beta1 parameter for Adam optimizer. Default is 0.9.
            beta2 (float, optional): Beta2 parameter for Adam optimizer. Default is 0.999.
            epsilon (float, optional): Epsilon parameter to prevent division by zero in Adam optimizer. Default is 1e-8.

        Returns:
            float: Mean squared error loss between predicted outputs and true labels.
        """
        AllOutputs, self.Parameters = self.optimiser(inputData, labels, useBatches, batchSize, alpha, beta1, beta2, epsilon)
        loss = MSELossFunction(AllOutputs, labels)
        return loss