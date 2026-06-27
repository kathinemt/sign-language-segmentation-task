DGS DOI: doi.org/10.25592/dgs.corpus-3.0-text-1984189
https://www.sign-lang.uni-hamburg.de/meinedgs/html/1984189_de.html

Gold tier: Lexem_Gebärde_r_B  |  Pred tier: SIGN
  Gold segments: 62
  Pred segments: 66
  Frame-level macro F1 (B/I/O): 0.5644
  IoU: 0.6073

Gold tier: Deutsche_Übersetzung_B  |  Pred tier: SENTENCE
  Gold segments: 17
  Pred segments: 1
  Frame-level macro F1 (B/I/O): 0.3680
  IoU: 0.9725

Ran as:
```
pose_to_segments --pose dgs_sample.pose --elan output.eaf
python stats.py --gold_eaf gold_label.eaf --pred_eaf output.eaf --gold-tier "Lexem_Gebärde_r_B" --pred-tier SIGN
python stats.py --gold_eaf gold_label.eaf --pred_eaf output.eaf --gold-tier "Deutsche_Übersetzung_B" --pred-tier SENTENCE
```

Visualizing results:
    Representing the F1 score and IoU doesn't make much sense since they are just scalars in range (0, 1).
    When it comes to visualizing model output I think one option would be a joint .eaf file with both the gold and predictor labels as 
    annotation tracks, so that any deviations in the predicted segments would be immediately visible. 
    However, this would obviously be clunky to do any further work with and also not much more useful aside from a quick first impression.
    Alternatively, something like a simple confusion matrix (e.g. scikit ConfusionMatrixDisplay) could show what type of error occurs most frequently.

Comments:
    On a sign level, the F1 score hasn't changed much from the basic E1-E4 models presented in the paper, but performs worse than the 
    models with depth=4. The IoU seems to be definitively worse than the baseline E1 (-0.06), and even more so when it comes to the depth=4 versions/
    tuned decoding versions (-0.9). I do find this lower score rather surprising considering the data I took was also from the DGS corpus, which
    was the training data.
    On the sentence level, something clearly went wrong. I tried running the model with other input .pose files as well, and none of them
    showed sentence segmentation. Considering that we know there was no proper segmentation done, it makes no sense to consider the F1 score/IoU.

