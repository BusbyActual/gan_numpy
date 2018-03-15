import numpy as np
import cv2

from activations import *

class GAN(object):

	def __init__(self):
		self.batch_size = 64
		self.epochs = 25
		self.learning_rate = 0.00002


		#init generator weights
		self.g_W0 = np.random.random((100,150)) * 2 - 1
		self.g_b0 = np.random.random((150)) * 2 - 1

		self.g_W1 = np.random.random((150,300)) * 2 - 1
		self.g_b1 = np.random.random((300)) * 2 - 1
		
		self.g_W2 = np.random.random((300,28*28)) * 2 - 1
		self.g_b2 = np.random.random((28*28)) * 2 - 1
		

		#init discriminator weights
		self.d_W0 = np.random.random((28*28,300)) * 2 - 1
		self.d_b0 = np.random.random((300)) * 2 - 1

		self.d_W1 = np.random.random((300,150)) * 2 - 1
		self.d_b1 = np.random.random((150)) * 2 - 1
		
		self.d_W2 = np.random.random((150,1)) * 2 - 1
		self.d_b2 = np.random.random((1)) * 2 - 1

	def discriminator(self, img):
		self.d_input = np.reshape(img, (self.batch_size, -1))

		self.d_h0 = np.matmul(self.d_input, self.d_W0)# + self.d_b0
		self.d_h0 = relu(self.d_h0)

		self.d_h1 = np.matmul(self.d_h0, self.d_W1)# + self.d_b1
		self.d_h1 = relu(self.d_h1)

		self.d_out = np.matmul(self.d_h1, self.d_W2)# + self.d_b2

		return self.d_out, sigmoid(self.d_out)

	def generator(self, z):

		self.g_h0 = np.matmul(z, self.g_W0) + self.g_b0
		self.g_h0 = relu(self.g_h0)

		self.g_h1 = np.matmul(self.g_h0, self.g_W1)# + self.g_b1
		self.g_h1 = relu(self.g_h1)

		self.g_h2 = np.matmul(self.g_h1, self.g_W2)# + self.g_b2
		self.g_out = sigmoid(self.g_h2)

		self.g_out = np.reshape(self.g_h2, (self.batch_size, 28, 28))
		
		return self.g_h2, self.g_out

	# generator backpropagation
	def backprop_gen(self, logit, output):
		output = np.reshape(output, (self.batch_size, -1))
		logit = np.tile(logit, [1, output.shape[-1]])
		logit = -1.0/logit

		err = logit*sigmoid(output, derivative=True)
		self.g_W2 += self.learning_rate*np.matmul(self.g_h1.T, err)	

		err = np.matmul(err, self.g_W2.T)
		err = err*relu(self.g_h1,derivative=True)
		self.g_W1 += self.learning_rate*np.matmul(self.g_h0.T, err)
		

		err = np.matmul(err, self.g_W1.T)
		err = err*relu(self.g_h0,derivative=True)
		self.g_W0 += self.learning_rate*np.matmul(self.z.T, err)
		
	# discriminator backpropagation 
	def backprop_dis(self, logit, output, real=True):
		if real:
			logit = -1.0/logit
		else:
			logit = 1.0/(1.0-logit)

		err = logit*sigmoid(output, derivative=True)
		self.d_W2 += self.learning_rate*np.matmul(self.d_h1.T, err)
		
		err = np.matmul(err, self.d_W2.T)
		err = err*relu(self.d_h1,derivative=True)
		self.d_W1 += self.learning_rate*np.matmul(self.d_h0.T, err)
		

		err = np.matmul(err, self.d_W1.T)
		err = err*relu(self.d_h0,derivative=True)
		self.d_W0 += self.learning_rate*np.matmul(self.d_input.T, err)
		

	def train(self):
		epsilon = 10e-4
		#we don't need labels.
		#just read images
		trainX, _, train_size = mnist_reader()
		
		batch_idx = train_size//self.batch_size
		for epoch in range(self.epochs):
			for idx in range(batch_idx):
				#prepare batch and input vector z
				train_batch = trainX[idx*self.batch_size:idx*self.batch_size + self.batch_size]
				self.z = np.random.uniform(-1,1,[self.batch_size,100])

				#forward pass
				g_logits, fake_img = self.generator(self.z)
				d_real_logits, d_real_output = self.discriminator(train_batch)
				d_fake_logits, d_fake_output = self.discriminator(fake_img)

				#calculate loss
				real_label = np.ones((self.batch_size, 1), dtype=np.float32)
				fake_label = np.zeros((self.batch_size, 1), dtype=np.float32)

				#cross entropy loss using sigmoid output
				#add epsilon in log to avoid overflow
				d_loss = -np.log(d_real_output+epsilon) + np.log(1 - d_fake_output+epsilon)

				g_loss = -np.log(d_fake_output+epsilon)

				#train discriminator
				#one for fake input, another for real input(?)
				self.backprop_dis(d_fake_logits, d_fake_output, real=False)
				self.backprop_dis(d_real_logits, d_real_output)
				
				#train generator twice
				self.backprop_gen(d_fake_logits, fake_img)
				self.backprop_gen(d_fake_logits, fake_img)

				img_tile(fake_img)

				print "Epoch [%d] Step [%d] G Loss:%.4f D Loss:%.4f"%(epoch, idx, np.sum(g_loss)/self.batch_size, np.sum(d_loss)/self.batch_size)


gan = GAN()
gan.train()	