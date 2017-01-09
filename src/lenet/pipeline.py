import tensorflow as tf
import tqdm

import nets.lenet as model
import sermanet_lecun.preprocess as preprocess

BATCH_SIZE = 50
EPOCHS = 60


def optimize(stack, encoded_y, learning_rate=1e-4):
    cross_entropy = tf.nn.softmax_cross_entropy_with_logits(stack, encoded_y)
    loss = tf.reduce_mean(cross_entropy)
    return tf.train.AdamOptimizer(learning_rate).minimize(loss)


def evaluate(stack, encoded_y):
    y_prediction = tf.nn.softmax(stack)
    prediction_match = tf.equal(tf.argmax(y_prediction, dimension=1), tf.argmax(encoded_y, dimension=1))
    return tf.reduce_mean(tf.cast(prediction_match, tf.float32))


def run(train_input, train_output, validation_input, validation_output, prediction_size):
    x = tf.placeholder(tf.float32, [None, 1024])
    x_4d = tf.reshape(x, [-1, 32, 32, 1])

    y = tf.placeholder(tf.int32, [None])
    classifier = tf.one_hot(y, prediction_size)

    net = model.stack(network_input=x_4d, network_input_depth=1, output_size=prediction_size)

    optimizer = optimize(net, classifier)
    evaluator = evaluate(stack=net, encoded_y=classifier)

    with tf.Session() as session:
        session.run(tf.global_variables_initializer())
        input_size = len(train_input)
        for epoch in range(EPOCHS):
            for batch in tqdm.tqdm(range(0, input_size, BATCH_SIZE), desc='Mini Batch Training'):
                input_batch, output_batch = preprocess.run(train_input[batch:batch+BATCH_SIZE]), train_output[batch:batch+BATCH_SIZE]
                session.run(optimizer, feed_dict={x: input_batch, y: output_batch})
            print("Training Epoch: {}, Accuracy: {}\n".format(epoch, session.run(evaluator, feed_dict={x: preprocess.run(validation_input), y: validation_output})))
        session.close()


