# -*- coding: utf-8 -*-
# shapes.py
import math

def create_diamond_shape(radius):
    """Beautiful diamond crystal - elegant and minimalist"""
    if radius < 2: return ['◇']
    r = int(radius)
    s = []
    
    scale = radius / 6.0
    
    for y in range(-r, r + 1):
        line = []
        for x in range(-r * 2, r * 2 + 1):
            dx, dy = x * 0.5, y
            
            # Diamond shape using Manhattan distance
            manhattan_dist = abs(dx) + abs(dy)
            
            # Layered diamond with different intensities
            if manhattan_dist <= 1.0 * scale:
                line.append('◆')
            elif manhattan_dist <= 2.2 * scale:
                line.append('◇')
            elif manhattan_dist <= 3.8 * scale:
                line.append('◊')
            elif manhattan_dist <= 5.0 * scale:
                # Subtle sparkles around the diamond
                if (int(dx * 3) + int(dy * 3)) % 3 == 0:
                    line.append('·')
                else:
                    line.append(' ')
            else:
                line.append(' ')
        s.append("".join(line))
    return s

def create_star_shape(radius):
    """Radiant star - inspiring and uplifting"""
    if radius < 2: return ['★']
    r = int(radius)
    s = []
    
    scale = radius / 6.0
    
    for y in range(-r, r + 1):
        line = []
        for x in range(-r * 2, r * 2 + 1):
            dx, dy = x * 0.5, y
            dist = math.sqrt(dx*dx + dy*dy)
            angle = math.atan2(dy, dx) + math.pi
            
            # 8-pointed star design
            star_rays = 8
            ray_angle = angle * star_rays / 2
            ray_intensity = (math.cos(ray_angle) + 1) / 2
            
            # Center core
            if dist <= 0.8 * scale:
                line.append('★')
            elif dist <= 2.0 * scale:
                # Inner star rays
                if ray_intensity > 0.7:
                    line.append('✦')
                elif ray_intensity > 0.4:
                    line.append('✧')
                else:
                    line.append(' ')
            elif dist <= 4.0 * scale:
                # Outer star rays
                if ray_intensity > 0.8:
                    line.append('*')
                elif ray_intensity > 0.6:
                    line.append('·')
                else:
                    line.append(' ')
            else:
                line.append(' ')
        s.append("".join(line))
    return s

def create_wave_flow_shape(radius):
    """Flowing waves - peaceful and rhythmic"""
    if radius < 2: return ['∿']
    r = int(radius)
    s = []
    
    scale = radius / 6.0
    
    for y in range(-r, r + 1):
        line = []
        for x in range(-r * 2, r * 2 + 1):
            dx, dy = x * 0.5, y
            dist = math.sqrt(dx*dx + dy*dy)
            
            # Multiple wave frequencies for organic flow
            wave1 = math.sin(dx * 1.2 + dy * 0.8) * 0.5
            wave2 = math.cos(dx * 0.8 + dy * 1.2) * 0.5
            wave3 = math.sin(dx * 2.0) * math.cos(dy * 2.0) * 0.3
            
            combined_wave = wave1 + wave2 + wave3
            
            max_dist = 4.5 * scale
            if dist <= max_dist:
                dist_factor = 1 - (dist / max_dist)
                intensity = (combined_wave + 1) * dist_factor
                
                if intensity > 1.2:
                    line.append('≋')
                elif intensity > 0.8:
                    line.append('∿')
                elif intensity > 0.5:
                    line.append('∼')
                elif intensity > 0.2:
                    line.append('~')
                else:
                    line.append(' ')
            else:
                line.append(' ')
        s.append("".join(line))
    return s

def create_tree_shape(radius):
    """Serene tree - growth and grounding"""
    if radius < 3: return ['🌳']
    r = int(radius)
    s = []
    
    scale = radius / 6.0
    
    for y in range(-r, r + 1):
        line = []
        for x in range(-r * 2, r * 2 + 1):
            dx, dy = x * 0.5, y
            dist = math.sqrt(dx*dx + dy*dy)
            
            # Tree structure: crown (top), trunk (bottom)
            crown_center_y = -r * 0.4
            trunk_center_y = r * 0.6
            
            # Tree crown (fractal-like branches)
            if dy <= crown_center_y + r * 0.6:
                crown_dist = math.sqrt(dx*dx + (dy - crown_center_y)**2)
                if crown_dist <= 2.5 * scale:
                    # Organic branch pattern
                    branch_pattern = math.sin(dx * 2) * math.cos(dy * 1.5)
                    if crown_dist <= 1.5 * scale or branch_pattern > 0.3:
                        line.append('♦' if crown_dist <= 1.0 * scale else '◆')
                    else:
                        line.append('·' if branch_pattern > 0 else ' ')
                else:
                    line.append(' ')
            # Tree trunk
            elif dy >= trunk_center_y - r * 0.4 and abs(dx) <= 0.3 * scale:
                line.append('█' if abs(dx) <= 0.2 * scale else '▌')
            else:
                line.append(' ')
        s.append("".join(line))
    return s

def create_crystal_shape(radius):
    """Sacred crystal - clarity and focus"""
    if radius < 2: return ['◈']
    r = int(radius)
    s = []
    
    scale = radius / 6.0
    
    for y in range(-r, r + 1):
        line = []
        for x in range(-r * 2, r * 2 + 1):
            dx, dy = x * 0.5, y
            dist = math.sqrt(dx*dx + dy*dy)
            angle = math.atan2(dy, dx) + math.pi
            
            # Hexagonal crystal structure
            hex_angle = angle * 3 / math.pi  # 6-fold symmetry
            hex_factor = math.cos(hex_angle) * 0.5 + 0.5
            
            # Crystal layers
            crystal_core = 1.0 * scale
            crystal_inner = 2.4 * scale
            crystal_outer = 4.0 * scale
            
            if dist <= crystal_core:
                line.append('◈')
            elif dist <= crystal_inner:
                if hex_factor > 0.7:
                    line.append('◇')
                elif hex_factor > 0.4:
                    line.append('◊')
                else:
                    line.append('·')
            elif dist <= crystal_outer:
                if hex_factor > 0.8:
                    line.append('·')
                else:
                    line.append(' ')
            else:
                line.append(' ')
        s.append("".join(line))
    return s

def create_infinity_shape(radius):
    """Infinity symbol - endless possibilities"""
    if radius < 2: return ['∞']
    r = int(radius)
    s = []
    
    scale = radius / 6.0
    
    for y in range(-r, r + 1):
        line = []
        for x in range(-r * 2, r * 2 + 1):
            dx, dy = x * 0.5, y
            
            # Infinity symbol (lemniscate) equation
            # (x² + y²)² = a²(x² - y²) where a = scale
            a_sq = (1.5 * scale) ** 2
            left_term = (dx*dx + dy*dy)**2
            right_term = a_sq * (dx*dx - dy*dy)
            
            # Distance from the infinity curve
            curve_dist = abs(left_term - right_term) / (a_sq * 4)
            
            if curve_dist < 0.3:
                line.append('∞')
            elif curve_dist < 0.6:
                line.append('∽')
            elif curve_dist < 1.0 and dx*dx + dy*dy <= (3 * scale)**2:
                line.append('·')
            else:
                line.append(' ')
        s.append("".join(line))
    return s

def create_mandala_shape(radius):
    """Sacred mandala - harmony and balance"""
    if radius < 2: return ['⦿']
    r = int(radius)
    s = []
    
    scale = radius / 6.0
    
    for y in range(-r, r + 1):
        line = []
        for x in range(-r * 2, r * 2 + 1):
            dx, dy = x * 0.5, y
            dist = math.sqrt(dx*dx + dy*dy)
            angle = math.atan2(dy, dx) + math.pi
            
            # Complex mandala pattern with multiple symmetries
            sym6 = math.cos(angle * 6) * 0.3 + 0.7  # 6-fold symmetry
            sym8 = math.cos(angle * 8) * 0.2 + 0.8  # 8-fold symmetry
            sym12 = math.cos(angle * 12) * 0.15 + 0.85  # 12-fold symmetry
            
            combined_sym = (sym6 + sym8 + sym12) / 3
            
            # Concentric rings
            if dist <= 0.6 * scale:
                line.append('⦿')
            elif dist <= 1.4 * scale and combined_sym > 0.8:
                line.append('●')
            elif dist <= 2.2 * scale and combined_sym > 0.75:
                line.append('○')
            elif dist <= 3.0 * scale and combined_sym > 0.7:
                line.append('◦')
            elif dist <= 4.0 * scale and combined_sym > 0.65:
                line.append('·')
            else:
                line.append(' ')
        s.append("".join(line))
    return s

def create_labyrinth_shape(radius):
    """Meditative labyrinth - journey inward"""
    if radius < 2: return ['⌬']
    r = int(radius)
    s = []
    
    scale = radius / 6.0
    
    for y in range(-r, r + 1):
        line = []
        for x in range(-r * 2, r * 2 + 1):
            dx, dy = x * 0.5, y
            dist = math.sqrt(dx*dx + dy*dy)
            angle = math.atan2(dy, dx) + math.pi
            
            # Spiral labyrinth pattern
            spiral_turns = 7  # Traditional 7-circuit labyrinth
            spiral_radius = dist / scale
            spiral_angle = angle + spiral_radius * 0.8
            
            # Determine which circuit we're in
            circuit = int(spiral_radius)
            path_position = (spiral_angle / (2 * math.pi)) % 1
            
            max_dist = 4.5 * scale
            if dist <= max_dist and circuit < spiral_turns:
                # Create path segments
                if circuit % 2 == 0:
                    # Path segments
                    if 0.1 < path_position < 0.9:
                        line.append('▪' if circuit < 2 else '·')
                    else:
                        line.append(' ')
                else:
                    # Wall segments  
                    if 0.2 < path_position < 0.8:
                        line.append('■' if circuit < 3 else '▫')
                    else:
                        line.append(' ')
            else:
                line.append(' ')
        s.append("".join(line))
    return s

def create_yin_yang_shape(radius):
    """Yin Yang - balance and harmony"""
    if radius < 2: return ['☯']
    r = int(radius)
    s = []
    
    scale = radius / 6.0
    circle_r = 3.5 * scale
    
    for y in range(-r, r + 1):
        line = []
        for x in range(-r * 2, r * 2 + 1):
            dx, dy = x * 0.5, y
            dist = math.sqrt(dx*dx + dy*dy)
            
            if dist <= circle_r:
                # Yin Yang logic
                is_yang = dx > 0
                
                # Small circles (eyes)
                upper_eye_dist = math.sqrt(dx**2 + (dy + circle_r/2)**2)
                lower_eye_dist = math.sqrt(dx**2 + (dy - circle_r/2)**2)
                
                # S-curve divider
                curve_boundary = math.sin(dy / circle_r * math.pi) * circle_r * 0.3
                
                if upper_eye_dist <= circle_r * 0.25:
                    # Upper eye (yin in yang)
                    line.append('●')
                elif lower_eye_dist <= circle_r * 0.25:
                    # Lower eye (yang in yin)
                    line.append('○')
                elif dx > curve_boundary:
                    # Yang side
                    line.append('○')
                else:
                    # Yin side
                    line.append('●')
            else:
                line.append(' ')
        s.append("".join(line))
    return s

def create_spiral_pattern(radius):
    """Spiral pattern using .-=*#@ characters"""
    if radius < 2: return ['@']
    r = int(radius)
    s = []
    
    scale = radius / 6.0
    chars = [' ', '.', ':', ';', '=', '*', '#', '@']
    
    for y in range(-r, r + 1):
        line = []
        for x in range(-r * 2, r * 2 + 1):
            dx, dy = x * 0.5, y
            dist = math.sqrt(dx*dx + dy*dy)
            angle = math.atan2(dy, dx) + math.pi
            
            # Spiral pattern
            spiral_factor = (dist * 0.8 + angle * 2.0) % (2 * math.pi)
            intensity = (math.sin(spiral_factor) + 1) / 2
            
            max_dist = 4.5 * scale
            if dist <= max_dist:
                char_idx = int(intensity * (len(chars) - 2)) + 1
                char_idx = min(char_idx, len(chars) - 1)
                line.append(chars[char_idx])
            else:
                line.append(' ')
        s.append("".join(line))
    return s

def create_zen_circle_shape(radius):
    """Perfect enso circle - smooth scaling"""
    if radius < 2: return ['○']
    r = int(radius)
    s = []
    
    # Scale circle to radius
    scale = radius / 6.0
    circle_r = 3.4 * scale
    stroke_width = 0.4 * scale
    
    for y in range(-r, r + 1):
        line = []
        for x in range(-r * 2, r * 2 + 1):
            dx, dy = x * 0.5, y
            dist = math.sqrt(dx*dx + dy*dy)
            angle = math.atan2(dy, dx)
            
            # Enso with subtle opening that scales
            opening_size = 0.3 * scale
            opening_start = -opening_size
            opening_end = opening_size
            
            # Circle stroke that scales with radius
            inner_r = circle_r - stroke_width
            outer_r = circle_r + stroke_width
            
            if inner_r <= dist <= outer_r:
                if not (opening_start <= angle <= opening_end):
                    # Brush stroke effect
                    mid_r = (inner_r + outer_r) / 2
                    if abs(dist - mid_r) < stroke_width * 0.3:
                        line.append('●')
                    else:
                        line.append('○')
                else:
                    # Opening gap - make it more visible with subtle indication
                    if dist <= circle_r * 0.9:
                        line.append('·')  # Subtle indication of the brush trail
                    else:
                        line.append(' ')
            else:
                line.append(' ')
        s.append("".join(line))
    return s