import numpy as np
import matplotlib.pyplot as plt
materials = {
    # Dictionaries of materials and their modulus of elasticity in GPa
    'Rubber' : 0.1,
    'Polyethylene' : 1,
    'PVC' : 4,
    'Nylon' : 4,
    'Acrylic' : 3.5,
    'Polycarbonate' : 2.6,
    'Wood' : 16,
    'Bamboo': 20,
    'Concrete' : 40,
    'Glass' : 90,
    'Magnesium Alloy' : 45,
    'Aluminum Alloy' : 72,
    'Brass' : 110,
    'Bronze' : 120,
    'Copper' : 130,
    'Cast Iron' : 170,
    'Titanium Alloy' : 120,
    'Stainless Steel' : 210,
    'Mild Steel' : 210,
    'Tool Steel' : 220,
    'Wrought Iron' : 210,
    'Nickel' : 200,
    'Tungsten' : 410,
    'Tungsten Carbide' : 700, 
    'Silicon Carbide' : 450,
    'Diamond' : 1200
}
# validation of data entered by the user
def validate_input(prompt, cast_type, condition, error_msg):
    while True:
        try:
            value = cast_type(input(prompt))
            if condition(value):
                return value
            else:
                print(error_msg)
        except:
            print("Please enter a number as suggested.")

Error_msg = "Please enter a number greater than 0"
choice = 'Y'
print("The following program is built to calculate the maximum deflection, and maximum bending moment for a simply supported beam for a number of point and uniformly distributed loads. Some consideration are taken such as the loads are always applied from the top and the hinge support is present on the left side and roller support on the right side of the beam.")
while choice.lower() != 'n':
    loads = []
    positions = []
    end_positions = []
    initial_input = validate_input("Press 1 for calculation of point load, 2 for calculation of uniformly distributed load: ", int, lambda v : v >0 and v < 3, "Please enter the number as instructed.")
    #Beam classification
    beam_length = validate_input("Enter the length of the beam in m: ", float , lambda v:v > 0, Error_msg)
    beam_division = validate_input("Enter the number of points the beam is divided into: ", int, lambda v:v > 0, Error_msg)
    points = np.linspace(0,beam_length,beam_division)
    beam_material = input("Enter the material of the beam: ")
    if beam_material in materials:
        E_GPa = materials[beam_material]
    else:
        print("The material cannot be found in our database.")
        E_GPa = validate_input("Enter the modulus of Elasticity in GPa: ", float, lambda v:v > 0, Error_msg)
    E = E_GPa * (10**9) #conversion to Pa
    beam_I_mm = validate_input("Enter the moment of Inertia of the beam in mm4: ", float, lambda v: v > 0, Error_msg)
    beam_I_m = beam_I_mm * (10 ** -12)

    if initial_input == 1:
        # Loads classification for point load
        no_of_loads = validate_input("Enter number of point loads on the beam: ", int, lambda v:v > 0, Error_msg)
        print("Serially enter the loads from left to the right along with the position.")
        for i in range(no_of_loads):
            load = validate_input(f"{i+1}. Enter the load in kN: ", float, lambda v:v > 0, Error_msg)
            position = validate_input("Enter the position of load from the left side in m: ", float, lambda v:v > 0 and v < beam_length, "The position should be greater than beam length, should be greater than the previous lengths and be greater than 0.")
            loads.append(load)
            positions.append(position)
        loads = np.array(loads)
        positions = np.array(positions)

        #Reaction Calculation and Print
        reaction_A = np.sum(loads * (beam_length - positions)) / beam_length
        reaction_B = np.sum(loads * positions) / beam_length

        print(f"Reaction at Hinge Support: {reaction_A} kN")
        print(f"Reaction at Roller Support: {reaction_B} kN")

        #Shear force per point calculation
        shear = np.full(len(points), reaction_A)
        for i in range(no_of_loads):
            shear -= np.where(points >= positions[i], loads[i], 0)
    
    #For uniformly distributed load
    else:
        no_of_loads = validate_input("Enter number of uniformly distributed loads on the beam: ", int, lambda v:v > 0, Error_msg)
        print("Serially enter the magnitude and positions of load from left to right.")
        for i in range(no_of_loads):
            mag_uniload = validate_input(f"{i + 1}. Enter the magnitude of uniformly distributed load in kN/m: ", float, lambda v: v > 0, Error_msg)
            starting_pos = validate_input("Enter the starting position of the UDL in m: ", float, lambda v : v >= 0, "Please enter a number greater than or equal to 0")
            ending_pos = validate_input("Enter the ending position of the UDL in m: ", float, lambda v : (v <= beam_length) and (v > starting_pos), "Ending position should be greater than starting_position and less than the beam length. ")
            loads.append(mag_uniload)
            positions.append(starting_pos)
            end_positions.append(ending_pos)
        loads = np.array(loads)
        positions = np.array(positions)
        end_positions = np.array(end_positions)
        #conversion to point load 
        point_load = loads * (end_positions - positions)
        position_point = (ending_pos + positions) / 2
        #reaction calculation
        reaction_B = np.sum(point_load * position_point) / beam_length
        reaction_A = np.sum(point_load) - reaction_B
        print(f"Reaction at A: {reaction_A} kN")
        print(f"Reaction at B: {reaction_B} kN")
        #Shear force, moment and deflection calculation
        shear = np.full(len(points), reaction_A)

        for w,start,end in zip(loads,positions,end_positions):
            inside_effect = np.where( (points>=start) & (points<=end), w * (points-start), 0)
            after_effect = np.where( points> end, w * (end-start), 0)
            shear -= (inside_effect + after_effect)
    
    #Calculation for BMD, curvature, slope and deflection for both
    dx = points[1] - points[0] 
    BMD = np.cumsum(shear * dx)
    BMD_Nm = BMD * 1000
    print(f"Maximum bending moment: {BMD.max():.2f} kNm")

    curvature = BMD_Nm / (E * beam_I_m)
    slope = np.cumsum(curvature * dx)
    deflection = np.cumsum(slope * dx)
    correction = (points / beam_length) * deflection[-1]
    deflection -= correction
    deflection *= 1000
    print(f"The maximum deflection: {np.max(np.abs(deflection)):.3f} mm")

    #Graph plot for deflection, Shear Force and Bending Moment Diagram
    fig, axs = plt.subplots(3,1, figsize = (12,16))

    axs[0].set_title("Deflection of a simply supported beam.")
    axs[0].plot(points, deflection, color = "#E4F000", linewidth = 2, label ="Deflection of beam")
    axs[0].set_ylabel("Deflection in mm")
    if initial_input == 1:
        for pos in positions:
            axs[0].axvline(x=pos, color = "red", linewidth = 2, linestyle = ":", label = "Position of Point Load.")
    else:
        for pos, end in zip(positions, end_positions):
            axs[0].vlines(x=pos, ymin = 0, ymax = 0.2, color = "red", linewidth = 2, linestyle = ":")
            axs[0].vlines(x=end, ymin = 0, ymax = 0.2, color = "red", linewidth = 2, linestyle = ":")
            axs[0].hlines(y= 0.2, xmin = pos, xmax = end, color = "red", linewidth = 2, linestyle = ":")
    axs[0].legend()
    axs[0].grid(True)

    axs[1].set_title("Shear force diagram")
    if initial_input == 1:
        axs[1].step(points, shear, color = "#05FFFF", linewidth = 2, label ="Shear force diagram")
    else:
        axs[1].plot(points, shear, color = "#05FFFF", linewidth = 2, label ="Shear force diagram")
    axs[1].fill_between(points, shear, 0, alpha = 0.3)
    axs[1].set_ylabel("Shear Force in kN")
    axs[1].legend()
    axs[1].grid(True)

    axs[2].set_title("Bending Moment Diagram")
    axs[2].plot(points, - BMD, color = "#4EF800", linewidth = 2, label ="Bending Moment Diagram")
    axs[2].fill_between(points, -BMD, 0, alpha = 0.3)
    axs[2].set_ylabel("Bending Moment in kNm")
    axs[2].set_xlabel("x ->")
    axs[2].legend()
    axs[2].grid(True)
    plt.tight_layout(pad = 2)
    plt.show()
    choice = input("Do you want to continue (Y/N)? ")