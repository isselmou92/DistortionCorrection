import nibabel as nib
import numpy as np
import matplotlib.pyplot as plt

# Load the first Jacobian determinant map

# mouse jacobian
# jacobian_img_1 = nib.load('b0_correction_analysis/data/phantom_jacobian/jacobian_determinant_b0.nii')
jacobian_img_1 = nib.load('b0_correction_analysis/data/mouse_data/mouse_phantom_b0_jacobian.nii')
jacobian_data_1 = jacobian_img_1.get_fdata()

# Load the second Jacobian determinant map

#mouse jacobian
# jacobian_img_2 = nib.load('b0_correction_analysis/data/phantom_jacobian/jacobian_determinant_no_b0.nii')
jacobian_img_2 = nib.load('b0_correction_analysis/data/mouse_data/mouse_only_b0_jacobian.nii')
jacobian_data_2 = jacobian_img_2.get_fdata()


# Compute the difference between the two Jacobian determinant maps
jacobian_difference = jacobian_data_1 - jacobian_data_2

# Compute statistics (mean difference, standard deviation, etc.)
mean_difference = np.mean(jacobian_difference)
std_difference = np.std(jacobian_difference)

# Save the difference map to a new NIfTI file
difference_img = nib.Nifti1Image(jacobian_difference, jacobian_img_1.affine)
# nib.save(difference_img, 'b0_correction_analysis/data/phantom_jacobian/jacobian_difference.nii')
nib.save(difference_img, 'b0_correction_analysis/data/mouse_jacobian/jacobian_difference_mouse.nii')
# Print out the comparison statistics
print(f"Mean difference in Jacobian determinant: {mean_difference}")
print(f"Standard deviation of difference: {std_difference}")

# Plot histograms of the two Jacobian determinant maps
plt.figure(figsize=(12, 6))
plt.hist(jacobian_data_1.ravel(), bins=50, alpha=0.5, label='B0 + Phantom', color='blue')
plt.hist(jacobian_data_2.ravel(), bins=50, alpha=0.5, label='B0', color='red')

plt.xlabel('Jacobian Determinant')
plt.ylabel('Frequency')
plt.legend(loc='upper right')
plt.title('Histogram of Jacobian Determinants of the Mouse')
plt.show()

# Plot the difference map
plt.figure(figsize=(8, 8))
plt.imshow(np.mean(jacobian_difference, axis=2), cmap='coolwarm', interpolation='nearest')
plt.colorbar(label='Difference in Jacobian Determinant')
plt.title('Mean Difference in Jacobian Determinant (Axial View)')
plt.show()

# Plot the distribution of the difference values
plt.figure(figsize=(10, 5))
plt.hist(jacobian_difference.ravel(), bins=50, alpha=0.75, color='purple')
plt.xlabel('Difference in Jacobian Determinant')
plt.ylabel('Frequency')
plt.title('Histogram of Differences in Jacobian Determinant')
plt.show()
