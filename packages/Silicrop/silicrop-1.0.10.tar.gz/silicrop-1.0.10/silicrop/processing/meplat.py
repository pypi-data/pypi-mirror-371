import numpy as np
import cv2
import matplotlib.pyplot as plt
from scipy.optimize import least_squares
from scipy.signal import find_peaks
import pandas as pd
from matplotlib.patches import Ellipse as MplEllipse

def fit_ellipse_to_contour(contour):
    """
    Fit an ellipse to a contour using least squares optimization.
    
    Args:
        contour (np.ndarray): Array of contour points (Nx2).
        
    Returns:
        tuple: (center_x, center_y, major_axis, minor_axis, angle_rad)
    """
    # Initial guess: use the bounding ellipse
    (center_x, center_y), (major_axis, minor_axis), angle_deg = cv2.fitEllipse(contour.astype(np.float32))
    angle_rad = np.radians(angle_deg)
    
    # Define the ellipse equation: (x-h)²/a² + (y-k)²/b² = 1
    def ellipse_residuals(params, points):
        h, k, a, b, theta = params
        x, y = points[:, 0], points[:, 1]
        
        # Rotate points to ellipse coordinate system
        x_rot = (x - h) * np.cos(theta) + (y - k) * np.sin(theta)
        y_rot = -(x - h) * np.sin(theta) + (y - k) * np.cos(theta)
        
        # Calculate residuals: distance from ellipse
        ellipse_eq = (x_rot**2 / a**2) + (y_rot**2 / b**2) - 1
        return ellipse_eq
    
    # Initial parameters: [center_x, center_y, major_axis, minor_axis, angle]
    initial_params = [center_x, center_y, major_axis/2, minor_axis/2, angle_rad]
    
    # Optimize using least squares
    result = least_squares(ellipse_residuals, initial_params, args=(contour,))
    
    if result.success:
        h, k, a, b, theta = result.x
        return h, k, a, b, theta
    else:
        # Fallback to OpenCV fit if optimization fails
        return center_x, center_y, major_axis/2, minor_axis/2, angle_rad


def draw_ellipse_fit(contour, ellipse_params, ax=None):
    """
    Draw the fitted ellipse on a matplotlib axis.
    
    Args:
        contour (np.ndarray): Original contour points
        ellipse_params (tuple): (center_x, center_y, major_axis, minor_axis, angle_rad)
        ax (matplotlib.axes.Axes): Axis to draw on, if None creates a new figure
    """
    h, k, a, b, theta = ellipse_params
    
    # Generate ellipse points
    t = np.linspace(0, 2*np.pi, 100)
    x_ellipse = a * np.cos(t)
    y_ellipse = b * np.sin(t)
    
    # Rotate and translate
    x_rot = x_ellipse * np.cos(theta) - y_ellipse * np.sin(theta) + h
    y_rot = x_ellipse * np.sin(theta) + y_ellipse * np.cos(theta) + k
    
    if ax is None:
        plt.figure(figsize=(10, 8))
        ax = plt.gca()
    
    # Plot original contour
    ax.plot(contour[:, 0], contour[:, 1], 'b-', linewidth=2)
    
    # Plot fitted ellipse
    ax.plot(x_rot, y_rot, 'r--', linewidth=3)
    
    # Plot center
    ax.plot(h, k, 'ro', markersize=8)
    
    # Plot major and minor axes
    major_end_x = h + a * np.cos(theta)
    major_end_y = k + a * np.sin(theta)
    minor_end_x = h + b * np.cos(theta + np.pi/2)
    minor_end_y = k + b * np.sin(theta + np.pi/2)
    
    ax.plot([h, major_end_x], [k, major_end_y], 'g-', linewidth=2)
    ax.plot([h, minor_end_x], [k, minor_end_y], 'm-', linewidth=2)
    
    ax.set_aspect('equal')
    ax.grid(True, alpha=0.3)
    ax.set_title(f'Ellipse Fit\nCenter: ({h:.1f}, {k:.1f})\nMajor: {a:.1f}, Minor: {b:.1f}\nAngle: {np.degrees(theta):.1f}°')
    
    return ax


def calculate_ellipse_deviations(contour, ellipse_params):
    """
    Calculate the deviation between contour points and the fitted ellipse.
    
    Args:
        contour (np.ndarray): Array of contour points (Nx2)
        ellipse_params (tuple): (center_x, center_y, major_axis, minor_axis, angle_rad)
        
    Returns:
        tuple: (deviations, angles, meplat_indices)
    """
    h, k, a, b, theta = ellipse_params
    
    # Generate a dense set of angles to sample the contour
    angles_deg = np.linspace(-180, 180, 360)  # 1 degree resolution
    angles_rad = np.radians(angles_deg)
    
    # Calculate theoretical ellipse radius for each angle
    ellipse_radius = a * b / np.sqrt((b * np.cos(angles_rad))**2 + (a * np.sin(angles_rad))**2)
    
    # For each angle, find the actual contour point at that angle
    actual_radius = np.zeros_like(angles_deg)
    
    # Transform contour points to ellipse coordinate system
    x, y = contour[:, 0], contour[:, 1]
    x_rot = (x - h) * np.cos(theta) + (y - k) * np.sin(theta)
    y_rot = -(x - h) * np.sin(theta) + (y - k) * np.cos(theta)
    
    # Calculate angles of contour points
    contour_angles = np.arctan2(y_rot, x_rot)
    contour_angles_deg = np.degrees(contour_angles)
    contour_radii = np.sqrt(x_rot**2 + y_rot**2)
    
    # For each sampling angle, find the closest contour point
    for i, target_angle in enumerate(angles_deg):
        # Find contour points within ±5 degrees of target angle
        angle_diff = np.abs(contour_angles_deg - target_angle)
        # Handle angle wrapping around ±180
        angle_diff = np.minimum(angle_diff, 360 - angle_diff)
        
        # Find points within tolerance
        tolerance = 5.0  # degrees
        valid_indices = np.where(angle_diff <= tolerance)[0]
        
        if len(valid_indices) > 0:
            # Take the point with radius closest to ellipse radius
            # This ensures we get the "outermost" point at this angle
            valid_radii = contour_radii[valid_indices]
            actual_radius[i] = np.max(valid_radii)  # Take the outermost point
        else:
            # If no points found, interpolate from nearby angles
            # Find the two closest contour angles
            angle_distances = np.abs(contour_angles_deg - target_angle)
            angle_distances = np.minimum(angle_distances, 360 - angle_distances)
            closest_indices = np.argsort(angle_distances)[:2]
            
            if len(closest_indices) >= 2:
                # Linear interpolation
                angle1, angle2 = contour_angles_deg[closest_indices]
                radius1, radius2 = contour_radii[closest_indices]
                
                # Handle angle wrapping
                if abs(angle2 - angle1) > 180:
                    if angle2 > angle1:
                        angle1 += 360
                    else:
                        angle2 += 360
                
                # Interpolate
                if abs(angle2 - angle1) > 0:
                    t = (target_angle - angle1) / (angle2 - angle1)
                    actual_radius[i] = radius1 + t * (radius2 - radius1)
                else:
                    actual_radius[i] = radius1
            else:
                actual_radius[i] = ellipse_radius[i]  # Fallback
    
    # Calculate deviations (positive = outside ellipse, negative = inside ellipse)
    deviations = actual_radius - ellipse_radius
    
    # Debug: vérifier les paramètres et déviations
    print(f"DEBUG - Ellipse params: center=({h:.1f},{k:.1f}), a={a:.1f}, b={b:.1f}, angle={np.degrees(theta):.1f}°")
    print(f"DEBUG - Deviations range: min={np.min(deviations):.2f}, max={np.max(deviations):.2f}, mean={np.mean(deviations):.2f}")
    print(f"DEBUG - Actual radius range: min={np.min(actual_radius):.2f}, max={np.max(actual_radius):.2f}")
    print(f"DEBUG - Ellipse radius range: min={np.min(ellipse_radius):.2f}, max={np.max(ellipse_radius):.2f}")
    
    # Save data to CSV for analysis
    df = pd.DataFrame({
        'index': np.arange(len(deviations)),
        'angle_deg': angles_deg,
        'deviation': deviations,
        'actual_radius': actual_radius,
        'ellipse_radius': ellipse_radius
    })
    csv_filename = 'deviations_analysis.csv'
    df.to_csv(csv_filename, index=False)
    print(f'Data saved to {csv_filename}')
    
    return deviations, angles_deg, np.arange(len(deviations))


def find_meplat_zones_by_area(contour, ellipse_params, min_zone_size=10, top_n=5, plot_mask=False):
    """
    Find meplat zones by calculating areas between zero crossings of the deviation curve.
    
    Args:
        contour (np.ndarray): Array of contour points (Nx2)
        ellipse_params (tuple): (center_x, center_y, major_axis, minor_axis, angle_rad)
        min_zone_size (int): Minimum number of consecutive points to consider a zone
        top_n (int): Number of top zones to return
        
    Returns:
        list: List of tuples (start_idx, end_idx, area, mean_deviation, zone_type)
    """
    deviations, angles, indices = calculate_ellipse_deviations(contour, ellipse_params)
    
    # --- Plot simple déviation vs angle ------------------------------------
    if plot_mask:
        import matplotlib.pyplot as plt
        plt.figure(figsize=(8,4))
        plt.plot(angles, deviations, 'b-', linewidth=1)
        plt.axhline(0, color='k', linestyle='--', linewidth=0.8)
        plt.xlabel('Angle (deg)')
        plt.ylabel('Deviation (px)')
        plt.title('Deviation vs. Angle')
        plt.grid(alpha=0.3)
        plt.tight_layout()
        plt.show()

    min_angle = np.min(angles)
    max_angle = np.max(angles)
        
    # Find zero crossings
    zero_crossings = []
    for i in range(1, len(deviations)):
        if (deviations[i-1] >= 0 and deviations[i] < 0) or (deviations[i-1] < 0 and deviations[i] >= 0):
            zero_crossings.append(i)
    
    
    # Add start and end if they're not already included
    if 0 not in zero_crossings:
        zero_crossings.insert(0, 0)
    if len(deviations) - 1 not in zero_crossings:
        zero_crossings.append(len(deviations) - 1)
    
    # Calculate areas between zero crossings
    zones = []
    for i in range(len(zero_crossings) - 1):
        start_idx = zero_crossings[i]
        end_idx = zero_crossings[i + 1]
        
        # Check if zone is large enough
        zone_size = end_idx - start_idx
        if zone_size >= min_zone_size:
            zone_deviations = deviations[start_idx:end_idx]
            zone_angles = angles[start_idx:end_idx]
            
            # Calculate total area from y=0 (integral of deviations)
            total_area = np.trapz(zone_deviations, zone_angles)
            mean_deviation = np.mean(zone_deviations)
            
            zones.append((start_idx, end_idx, total_area, mean_deviation, 'meplat'))
    
    # Sort zones by absolute area (largest first)
    zones.sort(key=lambda x: abs(x[2]), reverse=True)
    
    print(f"Found {len(zones)} zones")
    print("DEBUG - Zones BEFORE sorting by abs area:")
    for i, (start_idx, end_idx, area, mean_dev, zone_type) in enumerate(zones[:5]):
        print(f"  Zone {i+1}: {end_idx-start_idx} points, area: {area:.2f}, abs_area: {abs(area):.2f}, mean: {mean_dev:.2f}")
    
    print("DEBUG - Zones AFTER sorting by abs area:")
    for i, (start_idx, end_idx, area, mean_dev, zone_type) in enumerate(zones[:5]):
        print(f"  Zone {i+1}: {end_idx-start_idx} points, area: {area:.2f}, abs_area: {abs(area):.2f}, mean: {mean_dev:.2f}")
    
    # Merge zones that cross the -180°/180° boundary
    if len(zones) >= 2:
        # Find zones that are at the extremes
        extreme_zones = []
        for i, zone in enumerate(zones):
            start_idx, end_idx, area, mean_dev, zone_type = zone
            start_angle = angles[start_idx]
            end_angle = angles[end_idx-1]
            
            # Check if zone is at -180° or +180° extremes
            if start_angle <= -150 or end_angle >= 150:
                extreme_zones.append((i, zone, start_angle, end_angle))
        
        # If we have extreme zones, merge them
        if len(extreme_zones) >= 2:
            # Find the zone that starts at -180° and the one that ends at +180°
            minus_180_zone = None
            plus_180_zone = None
            
            for idx, zone, start_angle, end_angle in extreme_zones:
                if start_angle <= -150:
                    minus_180_zone = (idx, zone)
                if end_angle >= 150:
                    plus_180_zone = (idx, zone)
            
            # If we found both, merge them
            if minus_180_zone is not None and plus_180_zone is not None:
                minus_idx, minus_zone = minus_180_zone
                plus_idx, plus_zone = plus_180_zone
                
                # Merge the zones
                merged_start_idx = minus_zone[0]
                merged_end_idx = plus_zone[1]
                
                # Calculate merged area
                merged_deviations = deviations[merged_start_idx:merged_end_idx]
                merged_angles = angles[merged_start_idx:merged_end_idx]
                merged_total_area = np.trapz(merged_deviations, merged_angles)
                merged_mean_deviation = np.mean(merged_deviations)
                
                # Remove the original zones and add the merged one
                zones = [z for i, z in enumerate(zones) if i != minus_idx and i != plus_idx]
                zones.insert(0, (merged_start_idx, merged_end_idx, merged_total_area, merged_mean_deviation, 'meplat'))
                
                print(f"Merged zones at -180° and +180°: new area = {merged_total_area:.2f}")

        # --- Visualiser toutes les zones sur le graphe de déviation ---------
    if plot_mask:
        visualize_zones(contour, ellipse_params, zones)
        visualize_zones_on_mask(contour, ellipse_params, zones)
    
    if zones:
        # Trier par aire négative décroissante (plus grande aire négative = vrai méplat)
        zones_by_negative_area = sorted(zones, key=lambda x: x[2], reverse=False)  # False = ordre croissant, donc plus négatif en premier
        largest_zone_after_merge = zones_by_negative_area[0]
    else:
        largest_zone_after_merge = None

    # --- Afficher les angles de la largest zone APRÈS fusion -----------
    if largest_zone_after_merge:
        lz_start, lz_end, lz_area, _, _ = largest_zone_after_merge
        start_angle = angles[lz_start]
        end_angle = angles[lz_end-1]
        print(f"Largest zone AFTER merge: {start_angle:.1f}° → {end_angle:.1f}° (span: {end_angle-start_angle:.1f}°) - area: {lz_area:.2f}")

    # --- Plot largest_zone_before_merge sur le masque -------------------
    if plot_mask and largest_zone_after_merge:
        lz_start, lz_end, lz_area, _, _ = largest_zone_after_merge
        
        # Convert angle indices back to contour indices
        h, k, a, b, theta = ellipse_params
        x, y = contour[:, 0], contour[:, 1]
        x_rot = (x - h) * np.cos(theta) + (y - k) * np.sin(theta)
        y_rot = -(x - h) * np.sin(theta) + (y - k) * np.cos(theta)
        contour_angles = np.degrees(np.arctan2(y_rot, x_rot))
        
        # Find contour points within the largest zone angle range
        start_angle = angles[lz_start]
        end_angle = angles[lz_end-1]
        
        # Handle angle wrapping
        if end_angle < start_angle:
            # Zone crosses -180°/180° boundary
            mask = (contour_angles >= start_angle) | (contour_angles <= end_angle)
        else:
            mask = (contour_angles >= start_angle) & (contour_angles <= end_angle)
        
        lz_seg = contour[mask]

        # Construction du masque pour visualisation
        h_max = int(np.max(contour[:, 1])) + 5
        w_max = int(np.max(contour[:, 0])) + 5
        mask_full = np.zeros((h_max, w_max), dtype=np.uint8)
        cv2.fillPoly(mask_full, [contour.astype(np.int32)], 255)

        plt.figure(figsize=(6,6))
        plt.imshow(mask_full, cmap='gray')
        plt.plot(lz_seg[:,0], lz_seg[:,1], 'r-', linewidth=3)
        plt.title('Largest zone (after merge)')
        plt.axis('off')
        plt.show()

    # Keep only the zone with the largest absolute area (the meplat)
    if zones and largest_zone_after_merge:
        # Use the largest zone identified AFTER merging
        start_idx, end_idx, area, mean_deviation, zone_type = largest_zone_after_merge
        
        # Get the three contours:
        # 1. Original contour
        original_contour = contour.copy()
        
        # 2. Flat part (meplat zone) - convert angle indices to contour indices
        h, k, a, b, theta = ellipse_params
        x, y = contour[:, 0], contour[:, 1]
        x_rot = (x - h) * np.cos(theta) + (y - k) * np.sin(theta)
        y_rot = -(x - h) * np.sin(theta) + (y - k) * np.cos(theta)
        contour_angles = np.degrees(np.arctan2(y_rot, x_rot))
        
        # Find contour points within the largest zone angle range
        start_angle = angles[start_idx]
        end_angle = angles[end_idx-1]
        
        # Handle angle wrapping
        if end_angle < start_angle:
            # Zone crosses -180°/180° boundary
            mask = (contour_angles >= start_angle) | (contour_angles <= end_angle)
        else:
            mask = (contour_angles >= start_angle) & (contour_angles <= end_angle)
        
        flat_contour = contour[mask]
        flat_rect = None  # sera rempli plus bas

        # === Extension du méplat jusqu'à sortie du masque =========================
        if flat_contour.shape[0] >= 2:
            # Construction d'un mask binaire à partir du contour complet
            h_max = int(np.max(contour[:, 1])) + 2
            w_max = int(np.max(contour[:, 0])) + 2
            mask_full = np.zeros((h_max, w_max), dtype=np.uint8)
            cv2.fillPoly(mask_full, [contour.astype(np.int32)], 255)

            mask_bool = mask_full > 0

            # Ajustement linéaire (y = ax + b) sur le méplat
            x_flat = flat_contour[:, 0]
            y_flat = flat_contour[:, 1]
            if len(x_flat) >= 2:
                a, b = np.polyfit(x_flat, y_flat, 1)
                # Direction vector : selon la régression
                # Choisir deux points extrêmes connus pour direction initiale
                p_start = flat_contour[0]
                p_end   = flat_contour[-1]
                v = p_end - p_start
                norm = np.linalg.norm(v)
                if norm == 0:
                    v = np.array([1.0, 0.0])
                else:
                    v = v / norm

                def march(pt, direction, max_iter=5000, step=1.0):
                    x, y = pt.astype(float)
                    for _ in range(max_iter):
                        x += direction[0] * step
                        y += direction[1] * step
                        xi, yi = int(round(x)), int(round(y))
                        if xi < 0 or yi < 0 or xi >= w_max or yi >= h_max or not mask_bool[yi, xi]:
                            return np.array([x, y])
                    return np.array([x, y])

                p_neg = march(p_start, -v)
                p_pos = march(p_end, v)

                # === Calcul de l'épaisseur maximale perpendiculaire = extension latérale ===
                n_vec = np.array([-v[1], v[0]])  # vecteur normal
                n_vec = n_vec / (np.linalg.norm(n_vec) + 1e-8)
                # largeur perpendiculaire : max distance + 10 px
                t_fixed = 15

                # Points projetés extrêmes sur l'axe v (p_neg_base, p_pos_base)
                proj_vals = np.dot((flat_contour - p_start), v)
                p_neg_base = p_start + v * np.min(proj_vals)
                p_pos_base = p_start + v * np.max(proj_vals)

                # Extension le long de v jusqu'à ce que 3 coins franchissent le masque
                step_v = 1.0
                p_neg_ext = p_neg_base.copy()
                p_pos_ext = p_pos_base.copy()
                neg_done = False
                pos_done = False
                while True:
                    rect_pts = np.array([
                        p_neg_ext + n_vec * t_fixed,
                        p_neg_ext - n_vec * t_fixed,
                        p_pos_ext - n_vec * t_fixed,
                        p_pos_ext + n_vec * t_fixed
                    ])
                    # Évaluer coins hors masque
                    def is_out(pt):
                        x_, y_ = pt
                        xi, yi = int(round(x_)), int(round(y_))
                        return xi < 0 or yi < 0 or xi >= w_max or yi >= h_max or not mask_bool[yi, xi]

                    neg_out = [is_out(rect_pts[0]), is_out(rect_pts[1])]
                    pos_out = [is_out(rect_pts[2]), is_out(rect_pts[3])]
                    if all(neg_out):
                        neg_done = True
                    if all(pos_out):
                        pos_done = True
                    if neg_done and pos_done:
                        flat_rect = rect_pts.astype(np.float32)
                        break
                    # Avancer uniquement les côtés non terminés
                    if not neg_done:
                        p_neg_ext -= v * step_v
                    if not pos_done:
                        p_pos_ext += v * step_v

                # Ajout du rectangle au debug plot si demandé
                if plot_mask:
                    import matplotlib.pyplot as plt
                    plt.imshow(mask_full, cmap='gray')
                    rect_closed = np.vstack([flat_rect, flat_rect[0]])
                    plt.plot(rect_closed[:,0], rect_closed[:,1], 'r-', linewidth=2)
                    # ellipse fit superposée (à partir de ellipse_params)
                    h_e, k_e, a_e, b_e, theta_e = ellipse_params
                    ell_patch_dbg = MplEllipse((h_e, k_e), a_e*2, b_e*2, angle=np.degrees(theta_e), edgecolor='y', facecolor='none', linewidth=1.5)
                    plt.gca().add_patch(ell_patch_dbg)
                    plt.title('Rectangle méplat + ellipse')
                    plt.axis('off')
                    plt.show()

                # --- Extraire l'axe principal du rectangle --------------------
                # Milieux des côtés
                mids = [
                    (flat_rect[i] + flat_rect[(i+1)%4]) / 2 for i in range(4)
                ]
                # Deux couples de milieux opposés
                axis1 = (mids[0], mids[2])
                axis2 = (mids[1], mids[3])
                # Choisir la plus longue
                len1 = np.linalg.norm(axis1[1] - axis1[0])
                len2 = np.linalg.norm(axis2[1] - axis2[0])
                if len1 >= len2:
                    chosen_line = np.array(axis1, dtype=np.float32)
                else:
                    chosen_line = np.array(axis2, dtype=np.float32)

                flat_contour = chosen_line.copy()

                if plot_mask:
                    import matplotlib.pyplot as plt
                    plt.figure(figsize=(6,6))
                    plt.imshow(mask_full, cmap='gray')
                    plt.plot(flat_rect[[0,1,2,3,0],0], flat_rect[[0,1,2,3,0],1], 'r-', lw=1)
                    plt.plot(chosen_line[:,0], chosen_line[:,1], 'y-', lw=2)
                    plt.scatter(mids[0][0], mids[0][1], c='b')
                    plt.scatter(mids[1][0], mids[1][1], c='b')
                    plt.scatter(mids[2][0], mids[2][1], c='b')
                    plt.scatter(mids[3][0], mids[3][1], c='b')
                    # Points d'extrémité de flat_contour
                    plt.scatter(chosen_line[:,0], chosen_line[:,1], c='g', marker='x')
                    plt.title('Axe principal méplat')
                    plt.axis('off')
                    plt.show()

                axis_len = np.linalg.norm(chosen_line[1] - chosen_line[0])
                print(f"✅ Axe principal extrait, longueur ≈ {axis_len:.1f}px.")
                print("   Extrémités :", chosen_line)

                # Affichage debug
                print("✅ Méplat prolongé :", p_neg, "->", p_pos, ", width =", 2*t_fixed)

        # 3. Contour without the flat part = all other zones (separate)
        other_zones_contour = []
        flat_start, flat_end, _, _, _ = largest_zone_after_merge
        
        print(f"Flat zone indices: {flat_start} to {flat_end}")
        
        # Get all contour points that are NOT in the largest zone
        # Create a mask for all points NOT in the largest zone
        largest_zone_mask = np.zeros(len(contour), dtype=bool)
        
        # Mark points that are in the largest zone
        start_angle = angles[flat_start]
        end_angle = angles[flat_end-1]
        
        # Handle angle wrapping
        if end_angle < start_angle:
            # Zone crosses -180°/180° boundary
            largest_zone_mask = (contour_angles >= start_angle) | (contour_angles <= end_angle)
        else:
            largest_zone_mask = (contour_angles >= start_angle) & (contour_angles <= end_angle)
        
        # Get points NOT in the largest zone
        non_flat_mask = ~largest_zone_mask
        non_flat_contour = contour[non_flat_mask]
        
        # Split the non-flat contour into connected segments
        if len(non_flat_contour) > 0:
            # Find discontinuities in the contour indices
            contour_indices = np.where(non_flat_mask)[0]
            segments = []
            current_segment = [non_flat_contour[0]]
            
            for i in range(1, len(contour_indices)):
                # Check if indices are consecutive (with small tolerance for gaps)
                if contour_indices[i] - contour_indices[i-1] <= 2:  # Allow small gaps
                    current_segment.append(non_flat_contour[i])
                else:
                    # End of current segment
                    if len(current_segment) >= 5:  # Minimum segment size
                        segments.append(np.array(current_segment))
                    current_segment = [non_flat_contour[i]]
            
            # Add the last segment
            if len(current_segment) >= 5:
                segments.append(np.array(current_segment))
            
            other_zones_contour = segments
        

        if other_zones_contour:
            # Keep zones separate, don't connect them
            contour_without_flat = other_zones_contour  # List of separate contours
        else:
            contour_without_flat = []  # Empty list if no other zones
        
        return original_contour, flat_contour, contour_without_flat, flat_rect
    else:
        return contour, None, contour, None


def visualize_zones(contour, ellipse_params, zones):
    """
    Visualize the detected meplat zones on the deviation plot.
    
    Args:
        contour (np.ndarray): Original contour points
        ellipse_params (tuple): (center_x, center_y, major_axis, minor_axis, angle_rad)
        zones (list): List of meplat zones
    """
    deviations, angles, indices = calculate_ellipse_deviations(contour, ellipse_params)
    
    # Create the plot
    plt.figure(figsize=(15, 8))
    
    # Plot the full deviation curve
    plt.plot(angles, deviations, 'b-', linewidth=1, alpha=0.7, label='Deviations')
    plt.axhline(y=0, color='k', linestyle='--', alpha=0.5, label='Zero line')
    
    # Highlight each zone with different colors
    colors = ['red', 'orange', 'green', 'purple', 'brown', 'pink', 'gray', 'olive']
    
    for i, (start_idx, end_idx, area, mean_dev, zone_type) in enumerate(zones):
        if i < len(colors):
            color = colors[i]
        else:
            color = 'black'
        
        zone_angles = angles[start_idx:end_idx]
        zone_deviations = deviations[start_idx:end_idx]
        
        plt.plot(zone_angles, zone_deviations, color=color, linewidth=3, 
                label=f'Zone {i+1}: area={area:.1f}')
    
    plt.xlabel('Angle (degrees)')
    plt.ylabel('Deviation (pixels)')
    plt.title('Meplat Zones Detection')
    plt.grid(True, alpha=0.3)
    plt.show()


def visualize_zones_on_mask(contour, ellipse_params, zones):
    """
    Visualize the detected meplat zones directly on the mask.
    
    Args:
        contour (np.ndarray): Original contour points
        ellipse_params (tuple): (center_x, center_y, major_axis, minor_axis, angle_rad)
        zones (list): List of meplat zones
    """
    # Construction du masque pour visualisation
    h_max = int(np.max(contour[:, 1])) + 5
    w_max = int(np.max(contour[:, 0])) + 5
    mask_full = np.zeros((h_max, w_max), dtype=np.uint8)
    cv2.fillPoly(mask_full, [contour.astype(np.int32)], 255)
    
    # Convert contour to ellipse coordinate system for angle calculation
    h, k, a, b, theta = ellipse_params
    x, y = contour[:, 0], contour[:, 1]
    x_rot = (x - h) * np.cos(theta) + (y - k) * np.sin(theta)
    y_rot = -(x - h) * np.sin(theta) + (y - k) * np.cos(theta)
    contour_angles = np.degrees(np.arctan2(y_rot, x_rot))
    
    # Create the plot
    plt.figure(figsize=(12, 8))
    
    # Plot the mask
    plt.imshow(mask_full, cmap='gray')
    
    # Plot the full contour
    plt.plot(contour[:, 0], contour[:, 1], 'b-', linewidth=1, alpha=0.5, label='Full contour')
    
    # Highlight each zone with different colors
    colors = ['red', 'orange', 'green', 'purple', 'brown', 'pink', 'gray', 'olive']
    
    for i, (start_idx, end_idx, area, mean_dev, zone_type) in enumerate(zones):
        if i < len(colors):
            color = colors[i]
        else:
            color = 'black'
        
        # Convert angle indices to contour indices
        # Get the angles from the regular angle array (0-359)
        angles_deg = np.linspace(-180, 180, 360)
        start_angle = angles_deg[start_idx]
        end_angle = angles_deg[end_idx-1]
        
        # Handle angle wrapping
        if end_angle < start_angle:
            # Zone crosses -180°/180° boundary
            zone_mask = (contour_angles >= start_angle) | (contour_angles <= end_angle)
        else:
            zone_mask = (contour_angles >= start_angle) & (contour_angles <= end_angle)
        
        # Extract zone contour
        zone_contour = contour[zone_mask]
        
        if len(zone_contour) > 0:
            # Plot zone contour
            plt.plot(zone_contour[:, 0], zone_contour[:, 1], color=color, linewidth=3, 
                    label=f'Zone {i+1}: area={area:.1f}')
            
            # Mark start and end points
            plt.scatter(zone_contour[0, 0], zone_contour[0, 1], c=color, marker='o', s=50, edgecolors='white', linewidth=1)
            plt.scatter(zone_contour[-1, 0], zone_contour[-1, 1], c=color, marker='s', s=50, edgecolors='white', linewidth=1)
    
    # Plot ellipse fit
    h, k, a, b, theta = ellipse_params
    ell_patch = MplEllipse((h, k), a*2, b*2, angle=np.degrees(theta), 
                          edgecolor='yellow', facecolor='none', linewidth=2, alpha=0.7)
    plt.gca().add_patch(ell_patch)
    
    plt.title('Meplat Zones on Mask')
    plt.axis('off')
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    import os

    image_path = r"C:\Users\TM273821\Desktop\Database\mask.png"
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image not found: {image_path}")

    mask = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if mask is None:
        raise ValueError("Unable to read the image")

    _, thresh = cv2.threshold(mask, 127, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

    if not contours:
        raise ValueError("No contours found in the image")

    contour = max(contours, key=cv2.contourArea)[:, 0, :]

    # === Fit ellipse to contour
    print("Fitting ellipse to contour...")
    ellipse_params = fit_ellipse_to_contour(contour)
    h, k, a, b, theta = ellipse_params
    
    print(f"Ellipse parameters:")
    print(f"  Center: ({h:.2f}, {k:.2f})")
    print(f"  Major axis: {a:.2f}")
    print(f"  Minor axis: {b:.2f}")
    print(f"  Angle: {np.degrees(theta):.2f}°")
    print(f"  Eccentricity: {np.sqrt(1 - (b/a)**2):.3f}")

    # === Find meplat zones by area
    print("\nAnalyzing deviations by area...")
    original_contour, flat_contour, contour_without_flat, flat_rect = find_meplat_zones_by_area(contour, ellipse_params, min_zone_size=10, top_n=100, plot_mask=True)
    print(flat_contour)
    # === Visualize the three contours
    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(18, 6))
    
    # Original contour + ellipse fit
    ax1.imshow(mask, cmap='gray')
    ax1.plot(original_contour[:, 0], original_contour[:, 1], 'b-', linewidth=2)
    # ellipse_params correspond à ellipse_params
    center_e, axes_e, angle_e = ((h, k), (a*2, b*2), np.degrees(theta)) if 'h' in locals() else (ellipse_params[0:2], (ellipse_params[2]*2, ellipse_params[3]*2), np.degrees(ellipse_params[4]))
    ell_patch = MplEllipse(center_e, axes_e[0], axes_e[1], angle=angle_e, edgecolor='r', facecolor='none', linewidth=2)
    ax1.add_patch(ell_patch)
    ax1.set_title("Original Contour + Ellipse fit")
    ax1.axis('off')
    
    # Flat part (meplat)
    if flat_contour is not None:
        ax2.imshow(mask, cmap='gray')
        ax2.plot(flat_contour[:, 0], flat_contour[:, 1], 'r-', linewidth=3)
        ax2.scatter(flat_contour[:, 0], flat_contour[:, 1], c='y', marker='x', s=80)
        ax2.set_title("Flat Part (Meplat)")
        ax2.axis('off')
    else:
        ax2.text(0.5, 0.5, 'No meplat detected', ha='center', va='center', transform=ax2.transAxes)
        ax2.set_title("Flat Part (Meplat)")
        ax2.axis('off')
    
    # Contour without flat part
    ax3.imshow(mask, cmap='gray')
    if isinstance(contour_without_flat, list) and contour_without_flat:
        # Plot each separate contour
        for zone_contour in contour_without_flat:
            ax3.plot(zone_contour[:, 0], zone_contour[:, 1], 'g-', linewidth=2)
    elif len(contour_without_flat) > 0:
        # Single contour
        ax3.plot(contour_without_flat[:, 0], contour_without_flat[:, 1], 'g-', linewidth=2)
    ax3.set_title("Contour Without Flat Part")
    ax3.axis('off')
    
    plt.tight_layout()
    plt.show()
        
    