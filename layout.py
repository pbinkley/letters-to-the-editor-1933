import layoutparser as lp
import matplotlib.pyplot as plt
import matplotlib
import cv2 


model = lp.Detectron2LayoutModel('lp://PubLayNet/faster_rcnn_R_50_FPN_3x/config', 
                              extra_config=["MODEL.ROI_HEADS.SCORE_THRESH_TEST", 0.8],
                              label_map={0: "Text", 1: "Title", 2: "List", 3:"Table", 4:"Figure"}) 

img = cv2.imread("../letters-to-the-editor-1933/raw_images/1933-03-02_letters.jpg")
_, img = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY)

layout = model.detect(img)

viz = lp.draw_box(img, layout, box_width=3, show_element_id=True, box_alpha=0.3)
viz.save('output.jpg')
# import pdb; pdb.set_trace()

