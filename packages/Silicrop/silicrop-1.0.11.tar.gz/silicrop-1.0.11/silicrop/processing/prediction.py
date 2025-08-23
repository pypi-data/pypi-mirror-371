import torch
import numpy as np
import cv2
import time
from torchvision import transforms
from PIL import Image, ImageOps
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse as MplEllipse
import segmentation_models_pytorch as smp
import psutil
from silicrop.processing.crop import FitAndCrop
from silicrop.processing.rotate import Rotate
from silicrop.processing.meplat import find_meplat_zones_by_area


class EllipsePredictor:
    def __init__(self, model_path, fit_crop_widget=None):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.fit_crop_widget = fit_crop_widget

        # Load the DeepLabV3 model with ResNet-18 as the encoder
        self.model = smp.DeepLabV3(
            encoder_name="resnet18",  # Use ResNet-18 as the backbone
            encoder_weights="imagenet",  # Pre-trained weights on ImageNet
            classes=1  # Output channels (binary segmentation)
        ).to(self.device)

        # Load the model weights
        self.model.load_state_dict(torch.load(model_path, map_location=self.device))
        self.model.eval()

        # Define image transformations
        self.transform = transforms.Compose([
            transforms.Resize((256, 256)),
            transforms.ToTensor(),
        ])

        self.process = psutil.Process()

    def predict_mask(self, img_pil):
        """
        Predict the segmentation mask for the given image.
        """
        img_pil = ImageOps.exif_transpose(img_pil)
        img_tensor = self.transform(img_pil).unsqueeze(0).to(self.device)

        # Perform inference
        with torch.no_grad():
            output = self.model(img_tensor)
            mask = torch.sigmoid(output).squeeze().cpu().numpy()

        return mask

    def run_inference(self, img_path, dataset_type='200', plot=False, apply_projection=True):
        """
        Optimized version of the inference pipeline, suitable for batch usage.
        - No matplotlib.
        - Minimal memory & time overhead.
        """
        import time
        import os

        t_total = time.time()

        # 🧠 Charge image avec OpenCV (rapide)
        orig_img = cv2.imread(img_path)
        if orig_img is None:
            print(f"❌ Impossible de lire : {img_path}")
            return None, None, None

        h, w = orig_img.shape[:2]

        # 🔁 Conversion vers PIL uniquement pour le modèle
        img_rgb = cv2.cvtColor(orig_img, cv2.COLOR_BGR2RGB)
        img_pil = Image.fromarray(img_rgb)

        # 🤖 Prédiction (modèle)
        t0 = time.time()
        mask = self.predict_mask(img_pil)  # doit retourner image [0-1]
        print(f"  ⏱️ Modèle : {time.time() - t0:.3f}s")

        # 📉 Binarisation rapide
        mask_bin = (mask > 0.5).astype(np.uint8) * 255
        mask_resized = cv2.resize(mask_bin, (w, h), interpolation=cv2.INTER_NEAREST)

        # 🔎 Contours
        contours, _ = cv2.findContours(mask_resized, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        if not contours:
            print("❌ Aucun contour trouvé.")
            return None, None, None

        contour = max(contours, key=cv2.contourArea)
        contour = contour[:, 0, :]  # (N, 1, 2) → (N, 2)

        # 🔺 Fit ellipse initial pour obtenir ellipse_params
        if len(contour) < 5:
            print("❌ Pas assez de points pour fit ellipse.")
            return None, mask_resized, None

        initial_ellipse = cv2.fitEllipse(contour.reshape(-1, 1, 2))
        
        # Convert cv2.fitEllipse format to meplat format
        # cv2 format: (center, axes, angle) -> meplat format: (h, k, a, b, theta)
        center, axes, angle = initial_ellipse
        h, k = center
        a, b = axes[0]/2, axes[1]/2  # cv2 returns full axes, meplat expects half-axes
        theta = np.radians(angle)  # cv2 returns degrees, meplat expects radians
        ellipse_params = (h, k, a, b, theta)
        
        # 🔺 Traitement selon dataset
        if dataset_type == '150':
            original_contour, flat_part, contour_without_flat, flat_rect = find_meplat_zones_by_area(contour, ellipse_params, min_zone_size=25, top_n=100, plot_mask=False)
            print(flat_part)
            # Combine all non-flat parts into one contour for ellipse fitting
            if contour_without_flat:
                # Combine all contours by concatenating them
                curved_part = np.concatenate(contour_without_flat, axis=0)
            else:
                curved_part = original_contour.copy()
                
            if len(curved_part) < 5:
                print("❌ Pas assez de points (150).")
                return None, mask_resized, None

            ellipse = cv2.fitEllipse(curved_part.reshape(-1, 1, 2))
            
            # Extract only the 2 endpoints of the flat part for rotation
            if flat_part is not None and len(flat_part) >= 2:
                # Take the first and last points of the flat part
                points = [flat_part[0], flat_part[-1]]
            else:
                points = [flat_part[0], flat_part[1]] if flat_part is not None and len(flat_part) >= 2 else None

            # 🔍 VISU du méplat ---------------------------------------------------
            if plot:
                import matplotlib.pyplot as plt
                img_rgb_plot = cv2.cvtColor(orig_img, cv2.COLOR_BGR2RGB)
                fig, axes = plt.subplots(1, 6, figsize=(30, 5))
                ax1, ax2, ax3, ax4, ax5, ax6 = axes

                # Contour complet
                ax1.imshow(img_rgb_plot)
                ax1.plot(original_contour[:, 0], original_contour[:, 1], 'b-', linewidth=1)
                ax1.set_title('Original contour')
                ax1.axis('off')

                # Méplat
                ax2.imshow(img_rgb_plot)
                if flat_part is not None:
                    ax2.plot(flat_part[:, 0], flat_part[:, 1], 'r-', linewidth=2)
                ax2.set_title('Flat part (meplat)')
                ax2.axis('off')

                # Autres parties
                ax3.imshow(img_rgb_plot)
                for seg in contour_without_flat:
                    ax3.plot(seg[:, 0], seg[:, 1], 'g-', linewidth=1)
                ax3.set_title('Contour sans meplat')
                ax3.axis('off')

                ax4.axis('off')

                # rotation points après projection (sur image warpée)
                # recalcul rapide
                (cx, cy), (MA, ma), angle_e = ellipse
                diameter = int(max(MA, ma))
                pts1 = cv2.boxPoints(ellipse).astype(np.float32)
                pts2 = np.array([[0,0],[diameter-1,0],[diameter-1,diameter-1],[0,diameter-1]], dtype=np.float32)
                matrix = cv2.getPerspectiveTransform(pts1.astype(np.float32),
                                     pts2.astype(np.float32))
                rot_orig = np.array([points[0], points[-1]], dtype=np.float32).reshape(-1, 1, 2)
                rot_proj = cv2.perspectiveTransform(rot_orig, matrix).reshape(-1, 2)
                # montrer sur l’image warpée indépendante
                warped_img = cv2.warpPerspective(orig_img, matrix, (diameter, diameter))
                img_rgb_post = cv2.cvtColor(warped_img, cv2.COLOR_BGR2RGB)
                ax6.imshow(img_rgb_post)
                ax6.scatter(rot_proj[:,0], rot_proj[:,1], c='m', marker='x', s=80)
                ax6.set_title('Rotation points (projected)')
                ax6.axis('off')

                plt.tight_layout()
                plt.show()
        else:
            ellipse = initial_ellipse
            points = contour

        # --- Plot ellipse et points extrêmes ---------------------------------
        if plot:
            import matplotlib.pyplot as plt
            img_rgb_e = cv2.cvtColor(orig_img, cv2.COLOR_BGR2RGB)
            fig_e, ax_e = plt.subplots(figsize=(6, 6))
            ax_e.imshow(img_rgb_e)
            # Dessin ellipse
            center_e, axes_e, angle_e = ellipse
            ell_patch = MplEllipse(center_e, axes_e[0], axes_e[1], angle=angle_e,
                                  edgecolor='yellow', facecolor='none', linewidth=2)
            ax_e.add_patch(ell_patch)



        if apply_projection :
            self.fit_crop_widget.image = orig_img
            self.fit_crop_widget.ellipse_params = ellipse
            self.fit_crop_widget.process_and_display_corrected_image(points=points)

            pre_rot  = self.fit_crop_widget.processed_ellipse          # white_bg
            post_rot = self.fit_crop_widget.processed_widget.image     # white_bg après rotation

            return post_rot, mask_resized, ellipse, pre_rot            # ← on renvoie les deux
        else:
            result_img = orig_img.copy()
            processed_mask = mask_resized
            pre_rot = None  # pas de white_bg sans projection

        print(f"  ✅ Total inference : {time.time() - t_total:.3f}s")
        return result_img, processed_mask, ellipse, pre_rot


# ==== Debugging Entry Point ====
if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    import sys

    app = QApplication(sys.argv)

    model_path = r"C:\Users\TM273821\Desktop\Python_project\silicrop\silicrop\assets\DeepLabV3_150_flatspot_0.001_350_4_weights.pth"
    img_path = r"C:\Users\TM273821\Desktop\Database\200\Image\52.jpg"

    rotate_widget = Rotate()
    fit_crop = FitAndCrop(processed_label=rotate_widget, filter_150_button=True, filter_200_button=False, header=False)

    predictor = EllipsePredictor(model_path, fit_crop)
    img_rot, mask, ellipse, img_white_bg = predictor.run_inference(
        img_path, dataset_type='150', apply_projection=True , plot=True
    )

    # img_white_bg contient exactement le white_bg que tu cherches

    # --- Récupération des deux versions ----------------------------------------
    pre_rot  = fit_crop.processed_ellipse          # avant rotation
    post_rot = fit_crop.processed_widget.image     # après rotation (= rotate_widget.image)

    # --- Plot -------------------------------------------------------------------
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))

    # Avant rotation
    ax1.set_title("Avant rotation")
    ax1.axis("off")
    ax1.imshow(cv2.cvtColor(pre_rot, cv2.COLOR_BGR2RGB))

    # Après rotation
    ax2.set_title("Après rotation")
    ax2.axis("off")
    ax2.imshow(cv2.cvtColor(post_rot, cv2.COLOR_BGR2RGB))

    plt.tight_layout()
    plt.show()
