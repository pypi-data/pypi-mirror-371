def print_regressor_scores(y_preds, y_actuals, set_name=None):
    """Print the RMSE and MAE for the provided data

    Parameters
    ----------
    y_preds : Numpy Array
        Predicted target
    y_actuals : Numpy Array
        Actual target
    set_name : str
        Name of the set to be printed

    Returns
    -------
    """
    from sklearn.metrics import root_mean_squared_error as rmse
    from sklearn.metrics import mean_absolute_error as mae

    print(f"RMSE {set_name}: {rmse(y_actuals, y_preds)}")
    print(f"MAE {set_name}: {mae(y_actuals, y_preds)}")


def print_aucroc_score(y_preds, y_actuals, set_name=None):
    """Print the AUC-ROC score for the provided data

    Parameters
    ----------
    y_preds : Numpy Array or list
        Predicted probabilities or scores for the positive class
    y_actuals : Numpy Array or list
        Actual binary target labels (0 or 1)
    set_name : str
        Name of the set to be printed

    Returns
    -------
    """
    from sklearn.metrics import roc_auc_score

    aucroc = roc_auc_score(y_actuals, y_preds)
    print(f"AUC-ROC {set_name}: {aucroc}")



def plot_confusion_matrix(model, X, y, title="Confusion Matrix"):
    """
    Fits the model (if not already fitted) and plots the confusion matrix for given X, y.
    
    Parameters:
    model: Fitted classifier with a .predict() method
    X: Features
    y: True labels
    title: Title for the confusion matrix
    """
    from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay
    import matplotlib.pyplot as plt

    y_pred = model.predict(X)
    cm = confusion_matrix(y, y_pred)
    
    disp = ConfusionMatrixDisplay(confusion_matrix=cm)
    disp.plot(values_format='d', cmap='Blues')
    plt.title(title)
    plt.show()



# Below are functions for AUC-ROC and Precision Recall curves

import matplotlib.pyplot as plt
from sklearn.metrics import roc_curve, roc_auc_score, precision_recall_curve, average_precision_score

# AUC-ROC Curve
def plot_roc(y_true, y_probs, title=None):
    """
    Plot ROC curve for a single dataset.
    
    Parameters:
    - y_true: array-like, true labels (0 or 1)
    - y_probs: array-like, predicted probabilities for the positive class
    - title: optional, custom title
    """
    fpr, tpr, _ = roc_curve(y_true, y_probs)
    auc_score = roc_auc_score(y_true, y_probs)
    
    plt.figure(figsize=(6,6))
    plt.plot(fpr, tpr, lw=2, label=f'ROC (AUC = {auc_score:.4f})')
    plt.plot([0,1], [0,1], 'k--', label='Random Guess')
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title(title or 'ROC Curve')
    plt.legend()
    plt.grid(True)
    plt.show()

# Precision Recall Curve
def plot_pr(y_true, y_probs, positive_class_fraction=None, title=None):
    """
    Plot Precision-Recall curve for a single dataset.
    
    Parameters:
    - y_true: array-like, true labels (0 or 1)
    - y_probs: array-like, predicted probabilities for the positive class
    - positive_class_fraction: optional, baseline for PR curve (fraction of positives)
    - title: optional, custom title
    """
    precision, recall, _ = precision_recall_curve(y_true, y_probs)
    pr_auc = average_precision_score(y_true, y_probs)
    
    plt.figure(figsize=(6,6))
    plt.plot(recall, precision, lw=2, label=f'PR (AUC = {pr_auc:.4f})')
    if positive_class_fraction is not None:
        plt.hlines(y=positive_class_fraction, xmin=0, xmax=1, colors='red', linestyles='--', label='Baseline Precision')
    plt.xlabel('Recall')
    plt.ylabel('Precision')
    plt.title(title or 'Precision-Recall Curve')
    plt.legend()
    plt.grid(True)
    plt.show()

