

| Genre | Part A Accuracy | Part B Accuracy |
|---|---|---|
| Animation | 82.67% | 88.00% |
| Comedy | 79.33% | 70.67% |
| Documentary | 84.67% | 87.33% |
| Horror | 69.33% | 86.67% |
| Romance | 63.33% | 61.33% |
| Sci-Fi | 65.33% | 64.67% |
| **Overall** | 74.11% | 76.44% |

Then address these questions:

1. **Architecture choices**: Describe the image branch and tabular branch architectures you settled on. Why did you choose this structure? What did you try that didn't work as well?

In the image branch, I use 3 conv blocks with batch norm and ReLU, continually scaling up the dimension, with max pooling in between. At the end, there is an adaptive average pooling layer, then dropout and linear projection to the final output dimension. This structure is pretty straightforward, but performs better than when I tried it with just 2 conv layers. Dropout might not have been very necessary in this exact application, but I think it's generally a good idea to protect for getting more data in future, where it would be more helpful. For the tabular branch, the numeric part has a single dense layer with ReLU and dropout, while the embedding part has one table per field, mean pooling, and then concatenates them back together before joining with the numeric part.

2. **Overfitting**: Did you observe a gap between training and validation accuracy? At what point did it appear? What strategies did you use to combat it (dropout, weight decay, early stopping, smaller vocabulary, reduced model size, learning rate scheduling)? Which were most effective?

I didn't have a problem with it in the base runs at all. I noticed it strongly in my first attempt at the optional part A, when I just ran "fine_tune = True". That caused severe overfitting, and I realized the gradients from the untrained head were getting back-propagated into the pretrained backbone and screwing it up. To fix that I changed it to two phases of training, 5 epochs each, and only unfreezing the layer4 in ResNet in the second half.

3. **Part A vs. Part B**: How did your custom CNN compare to the pretrained ResNet18? Did transfer learning help, and if so, in what way (higher accuracy, faster convergence, less overfitting)?

ResNet improved accuracy slightly overall, but I noticed it varied by class - for example the accuracy for Horror was much better than the custom CNN, but much worse for Comedy. In general I'd say it was a good call to use ResNet, but I'd like to try it with more data or a slower learning rate to see if I could tease out the class differences.

4. **Tabular branch insights**: Which metadata features seemed most useful for genre prediction? Look at the per-class accuracy table — which genres did the model struggle with most? Does that make sense given the available features? If you tried ablations (tabular-only or image-only), what did you learn?

Documentaries and animations were picked up most often, which makes sense given that the model had access to production companies (Pixar or Dreamworks would be a good indicator of animation) and directors (documentarians tend to stick to their lane). On the other end, it makes sense that comedy and sci-fi were harder, since there wouldn't be much of a difference in actors, budgets, etc. compared to other genres. I noticed very similar results in the tabular-only run - documentaries and animations retained high accuracy, while in the image-only run, the model had no idea what a documentary poster looked like.

5. **What would you do differently?** If you had more compute time or training data, what would you try next?

More epochs with a slightly lower learning rate, I think. I messed around with it a few times and couldn't find one I really loved. And, I think that a decent image-only model could totally be done; it would just have to be architected much more carefully.

6. *(Optional — only if you completed optional extensions)* **Optional extensions**: For each optional experiment you ran, briefly describe what you tried, what result you got, and how it compared to your Part A baseline.

| Genre | Fine-Tuned Accuracy | Tabular-Only Accuracy | Image-Only Accuracy |
|---|---|---|---|
| Animation | 86.00% | 86.67% | 74.00% |
| Comedy | 66.67% | 68.67% | 39.33% |
| Documentary | 84.67% | 82.00% | 16.67% |
| Horror | 74.00% | 68.00% | 53.33% |
| Romance | 70.00% | 62.67% | 52.00% |
| Sci-Fi | 74.00% | 62.00% | 40.67% |
| **Overall** | 75.89% | 71.67% | 46.00% |

The fine-tuned version still did well, but not quite as good as the original Part B. I think it could be improved with more careful freezing/unfreezing, but that would just require experimentation with a bunch of different options.

As discussed before, the baseline model seemed to pick up on a lot of metadata to help it learn, evidenced by the fact that the tabular-only version was pretty close to it in accuracy, while the image-only version was way off.