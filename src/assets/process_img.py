import cv2
import numpy as np
import base64
import asyncio
from js import fetch
import requests
  
def scattering_from_gray_analytic(img):
      
      center1 = 0.15
      slope1 = 5
      amp1 = 0.061
      offset = - 0.04
      value_at_0 = np.tanh((0.0-center1) * slope1) + offset # Value of the function at 0.0
      value_at_1 = np.tanh((1.0-center1) * slope1) # Value of the function at 1.0
      tanh_img_1= amp1 * (np.tanh((img - center1) * slope1) - value_at_0) / (abs(value_at_0) + abs(value_at_1))
  
      center2 = 0.85
      slope2 = 16
      amp2 = 0.03
      value_at_0 = np.tanh((0.0-center2) * slope2) 
      value_at_1 = np.tanh((1.0-center2) * slope1) 
      tanh_img_2= amp2 * (np.tanh((img - center2) * slope2) - value_at_0) / (abs(value_at_0) + abs(value_at_1))
  
      scattering_img = tanh_img_1 + tanh_img_2
      return scattering_img
  
def absorption_from_gray_analytic(img):
  
      center1 = 0.375
      slope1 = 4.4
      amp1 = 0.06
      value_at_0 = np.tanh((0.0-center1) * slope1) # Value of the function at 0.0
      value_at_1 = np.tanh((1.0-center1) * slope1) # Value of the function at 1.0
      absorption_img = amp1 - amp1 * (np.tanh((img - center1) * slope1) - value_at_0) / (abs(value_at_0) + abs(value_at_1))
  
      return absorption_img
  
def weiner_algorithm(img_vis, img_IR, img_A, img_S, alpha = 1, beta = 1):
      
      img_UD = img_IR - (beta * cv2.multiply(img_vis, img_S)) ** (alpha * img_A) + 1
  
      # Normalizing the resulting image between 0 and 1
      img_UD = img_UD - np.amin(img_UD)
      img_UD = np.divide(img_UD, np.amax(img_UD))
  
      return img_UD
  
def generate_enhanced_underdrawing_image(img_vis, img_IR, alpha, beta):
  
      # The images pixel values are normalized to 1:
      img_vis_nrm = np.divide(img_vis, np.amax(img_vis))
      img_IR_nrm = np.divide(img_IR, np.amax(img_IR))
  
      # Computing intermediate images:
      img_S = scattering_from_gray_analytic(img_vis_nrm)
      img_A = absorption_from_gray_analytic(img_vis_nrm)
  
      # Computing the enhanced underdrawing image:
      img_UD = weiner_algorithm(img_vis_nrm, img_IR_nrm, img_A, img_S, alpha, beta)
      
      # Re-converting the image in 8-bits
      img_UD =  np.uint8(img_UD * 255)
  
      return img_UD
  
async def process_image():

      url_vis = r'${url_vis}'
      resp_vis = requests.get(url_vis, stream=True).raw
      image_vis = np.asarray(bytearray(resp_vis.read()), dtype="uint8")
      img_vis = cv2.imdecode(image_vis, 0) # 0 for directly reading as grayscale image
  
      url_IR = r'${url_IR}'
      resp_IR = requests.get(url_IR, stream=True).raw
      img_IR = np.asarray(bytearray(resp_IR.read()), dtype="uint8") # 0 for directly reading as grayscale image
      img_IR = cv2.imdecode(img_IR, 0)
  
      # The following two parameters should be adjustable wwith sliders:
      alpha = 1.20 # Free parameter 1
      beta = 0.8 # Free parameter 2
      
      # Calling the main function to execute the algorithm   
      img_UD = generate_enhanced_underdrawing_image(img_vis, img_IR, alpha, beta)
  
      # Path to write the resulting image
      _, buffer = cv2.imencode(".jpg", img_UD)
      data_url = base64.b64encode(buffer).decode("ascii")
      jpg_as_text = f"data:image/jpg;base64,{data_url}"
      
      return jpg_as_text
  
async def main():
        result = await process_image()
        return result
  
asyncio.ensure_future(main())