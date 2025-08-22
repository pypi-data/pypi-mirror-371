"""
Ths module contains the reaction model functions $f(\alpha)$
obtained from: 
    Journal of Hazardous Materials 364 (2019) 539–547
    Journal of Thermal Analysis and Calorimetry (2018) 134:1575–1587
"""
import numpy as np

## Power Laws

### P4: $ f\left(\alpha\right) = 4 \alpha^{3/4} $

def P4(a,integral = False):
    """
    Power Law (P4) model
    
    Parameters:   a : (\alpha) Conversion degree value.
    
    Returns:    f(a): Reaction model evaluated on the conversion degree
    """
    if integral == True:
        return a**(1/4)
    else:
        return 4*(a**(3/4))

### P3: $f\left(\alpha\right) = 3\alpha^{2/3}$

def P3(a,integral = False):
    """
    Power Law (P3) model
    
    Parameters:   a : (\alpha) Conversion degree value.
    
    Returns:    f(a): Reaction model evaluated on the conversion degree
    """
    if integral == True:
        return a**(1/3)
    else:
        return 3*(a**(2/3))

### P2: $f\left(\alpha\right) = 2\alpha^{1/2}$

def P2(a, integral = False):
    """
    Power Law (P2) model
    
    Parameters:   a : (\alpha) Conversion degree value.
    
    Returns:    f(a): Reaction model evaluated on the conversion degree
    """
    if integral == True:
        return a**(1/2)
    else:
        return 2*(a**(1/2))

### P2/3: $f\left(\alpha\right) = \frac{2}{3}\alpha^{-1/2}$

def P2_3(a, integral = False):
    """
    Power Law (P2/3) model
    
    Parameters:   a : (\alpha) Conversion degree value.
    
    Returns:    f(a): Reaction model evaluated on the conversion degree
    """
    if integral == True:
        return a**(3/2)
    else:
        return (2/3)*(a**(-1/2))

## Diffusion

### One dimensional D1: $f\left(\alpha\right) = \frac{1}{2}\alpha^{-1}$

def D1(a, integral = False):
    """
    One dimensional diffusion model (D1)
    
    Parameters:   a : (\alpha) Conversion degree value.
    
    Returns:    f(a): Reaction model evaluated on the conversion degree
    """
    if integral == True:
        return a**2
    else:
        return (1/2)*(a**(-1))

### Two dimensional D2: $f\left(\alpha\right) = \left[-\ln{\left(1-\alpha\right)}\right]^{-1}$

def D2(a, integral = False):
    """
    Two dimensional diffusion model (D2)
    
    Parameters:   a : (\alpha) Conversion degree value.
    
    Returns:    f(a): Reaction model evaluated on the conversion degree
    """
    if integral == True:
        return ((1-a)*np.log(1-a)) + a
    else:
        return 1/((-1)*np.log(1-a))

### Two dimensional G7: $f\left(\alpha\right) = 4{(1 - a)[1 - (1 - a)1/2]}1/2$

def G7(a, integral = False):
    """
    Two dimensional diffusion model (G7)
    
    Parameters:   a : (\alpha) Conversion degree value.
    
    Returns:    f(a): Reaction model evaluated on the conversion degree
    """
    if integral == True:
        return (1 - ((1 - a)**(1/2)))**(1/2)
    else:
        return 4*((1 - a)*(1 - ((1 - a)**(1/2))))**(1/2)

### Three dimensional D3 (Jander equation) : $f\left(\alpha\right) = \frac{3}{2}\left(1-\alpha\right)^{2/3}\left[1-\left(1-\alpha\right)^{1/3}\right]^{-1}$

def D3(a, integral = False):
    """
    Three dimensional diffusion model (D3) Jander equation
    
    Parameters:   a : (\alpha) Conversion degree value.
    
    Returns:    f(a): Reaction model evaluated on the conversion degree
    """
    if integral == True:
        return (1-((1-a)**(1/3)))**2
    else:
        return (3/2)*((1-a)**(2/3))*(1/(1-((1-a)**(1/3))))

### Three dimensional D4 (Ginstling-Brounshtein equation): $f\left(\alpha\right) = \frac{3}{2}\left(1-\alpha\right)^{2/3}\left[1-\left(1-\alpha\right)^{1/3}\right]^{-1}$

def D4(a, integral = False):
    """
    Three dimensional diffusion model (D4) Ginstling-Brounshtein equation
    
    Parameters:   a : (\alpha) Conversion degree value.
    
    Returns:    f(a): Reaction model evaluated on the conversion degree
    """
    if integral == True:
        return 1 - ( 2*a/3 ) - (1-a)**(2/3)
    else:
        return 3/(2*(((1-a)**(-1/3)) -1))

### Three dimensional (D5): $f\left(\alpha\right) = (3/2)(1 - a)4/3[- 1 ? (1 - a)-1/3]-1$

def D5(a, integral = False):
    """
    Three dimensional diffusion model (D5) 
    
    Parameters:   a : (\alpha) Conversion degree value.
    
    Returns:    f(a): Reaction model evaluated on the conversion degree
    """
    if integral == True:
        return (((1 - a)**(-1/3)) - 1)**2
    else:
        return (3/2)*((1 - a)**(4/3)) / (- 1 + ((1 - a)**(-1/3)))

### Three dimensional (D6): $f\left(\alpha\right) = (3/2)(1 ? a)2/3[- 1 ? (1 ? a)1/3]-1$

def D6(a, integral = False):
    """
    Three dimensional diffusion model (D6) 
    
    Parameters:   a : (\alpha) Conversion degree value.
    
    Returns:    f(a): Reaction model evaluated on the conversion degree
    """
    if integral == True:
        return (((1 + a)**(1/3)) - 1)**2
    else:        
        return (3/2)*((1 + a)**(2/3)) / (- 1 + ((1 + a)**(1/3))) 

### Three dimensional (D7): $f\left(\alpha\right) = (3/2)[1 - (1 ? a)-1/3]-1$

def D7(a, integral = False):
    """
    Three dimensional diffusion model (D7) 
    
    Parameters:   a : (\alpha) Conversion degree value.
    
    Returns:    f(a): Reaction model evaluated on the conversion degree
    """
    if integral == True:
        return 1 + (2*a/3) - ((1 + a)**(2/3))
    else:
        return (3/2) / (1 - ((1 + a)**(-1/3))) 

### Three dimensional (D8): $f\left(\alpha\right) = (3/2)(1 ? a)4/3[1 - (1 ? a)-1/3]-1$

def D8(a, integral = False):
    """
    Three dimensional diffusion model (D8) 
    
    Parameters:   a : (\alpha) Conversion degree value.
    
    Returns:    f(a): Reaction model evaluated on the conversion degree
    """
    if integral == True:
        return (((1 + a)**(-1/3)) - 1)**2
    else:
        return (3/2)*((1 + a)**(4/3)) / (1 - ((1 + a)**(-1/3)))                  

### Three dimensional (G8): $f\left(\alpha\right) = 6(1 - a)2/3[1 - (1 - a)1/3]1/2$

def G8(a, integral = False):
    """
    Three dimensional diffusion model (G8) 
    
    Parameters:   a : (\alpha) Conversion degree value.
    
    Returns:    f(a): Reaction model evaluated on the conversion degree
    """
    if integral == True:
        return (1 - (1 - a) )**(1/2)
    else:
        return 6*((1 - a)**(2/3))*((1 - ((1 - a)**(1/3)))**(1/2))

## Zero Order (F0): $f\left(\alpha\right) = 1

def F0(a, integral = False):
    """
    Zero order model (F)
    
    Parameters:   a : (\alpha) Conversion degree value.
    
    Returns:    f(a): Reaction model evaluated on the conversion degree
    """
    if integral == True:
        return a
    else:
        return 1

## One-third Order (F1/3): $f\left(\alpha\right) = (3/2)(1 - a)1/3$

def F1_3(a, integral = False):
    """
    One-third order model (F1/3)
    
    Parameters:   a : (\alpha) Conversion degree value.
    
    Returns:    f(a): Reaction model evaluated on the conversion degree
    """
    if integral == True:
        return 1 - ((1 - a)**(2/3))
    else:
        return (3/2)*((1 - a)**(1/3))

## Three-fourths Order (F3/4): $f\left(\alpha\right) = 4(1 - a)3/4$

def F3_4(a, integral = False):
    """
    Three-fourths order model (F3/4)
    
    Parameters:   a : (\alpha) Conversion degree value.
    
    Returns:    f(a): Reaction model evaluated on the conversion degree
    """
    if integral == True:
        return 1 - ((1 - a)**(1/4))
    else:
        return 4*((1 - a)**(3/4))

## Mampel (F1): $f\left(\alpha\right) = 1-\alpha$ 

def F1(a, integral = False):
    """
    Mampel (First order) model (F1)
    
    Parameters:   a : (\alpha) Conversion degree value.
    
    Returns:    f(a): Reaction model evaluated on the conversion degree
    """
    if integral == True:
        return -(np.log(1-a))
    else:
        return 1-a

## Three-halves Order (F3/2)

def F3_2(a, integral = False):
    """
    Three-halves order model (F3/2)

    Parameters:   a : (\alpha) Conversion degree value.

    Returns:    f(a): Reaction model evaluated on the conversion degree
    """
    if integral == True:
        return 2*(((np.log(1-a))**(-1/2))-1)
    else:
        return (1-a)**(3/2)

## Second Order (F3/2)

def F2(a, integral = False):
    """
    Second order model (F2)

    Parameters:   a : (\alpha) Conversion degree value.

    Returns:    f(a): Reaction model evaluated on the conversion degree
    """
    if integral == True:
        return (1 / (1-a)) -1
    else:
        return (1-a)**(2)

## Third Order (F3)

def F3(a, integral = False):
    """
    Third order model (F3)

    Parameters:   a : (\alpha) Conversion degree value.

    Returns:    f(a): Reaction model evaluated on the conversion degree
    """
    if integral == True:
        return (1/2)*(((1-a)**(-2))-1)
    else:
        return (1-a)**(3)

## Fourth Order (F4)

def F4(a, integral = False):
    """
    Third order model (F4)

    Parameters:   a : (\alpha) Conversion degree value.

    Returns:    f(a): Reaction model evaluated on the conversion degree
    """
    if integral == True:
        return ((1 - a)**(-3)) - 1
    else:
        return (1/3)*((1 - a)**4)

## Order (G1)

def G1(a, integral = False):
    """
    Order model (G1)

    Parameters:   a : (\alpha) Conversion degree value.

    Returns:    f(a): Reaction model evaluated on the conversion degree
    """
    if integral == True:
        return 1 - ((1 - a)**2)
    else:
        return 1 / (2 * (1 - a))

## Order (G2)

def G2(a, integral = False):
    """
    Order model (G2)

    Parameters:   a : (\alpha) Conversion degree value.

    Returns:    f(a): Reaction model evaluated on the conversion degree
    """
    if integral == True:
        return 1 - ((1 - a)**3)
    else:
        return 1 / (3 * ((1 - a)**2))

## Order (G3)

def G3(a, integral = False):
    """
    Order model (G3)

    Parameters:   a : (\alpha) Conversion degree value.

    Returns:    f(a): Reaction model evaluated on the conversion degree
    """
    if integral == True:
        return 1 - ((1 - a)**4)
    else:
        return 1 / (4 * ((1 - a)**3))

## Avrami-Erofeev

### A3/2: $f\left(\alpha\right) = (3/2)(1-\alpha)[-ln(1-\alpha)]^(1/3)$

def A3_2(a, integral = False):
    """
    Avrami-Erofeev (A3/2) model 
    
    Parameters:   a : (\alpha) Conversion degree value.
    
    Returns:    f(a): Reaction model evaluated on the conversion degree
    """
    if integral == True:
        return (-np.log(1-a))**(2/3)
    else:
        return (3/2)*(1-a)*((-np.log(1-a))**(1/3))

### A4: $f\left(\alpha\right) = 4\left(1-\alpha\right)\left[\ln{\left(1-\alpha\right)}\right]^{3/4}$

def A4(a, integral = False):
    """
    Avrami-Erofeev (A4) model 
    
    Parameters:   a : (\alpha) Conversion degree value.
  
    Returns:    f(a): Reaction model evaluated on the conversion degree
    """
    if integral == True:
        return (-np.log(1-a))**(1/4)
    else:
        return 4*(1-a)*((-np.log(1-a))**(3/4))

### A3: $f\left(\alpha\right) = 3\left(1-\alpha\right)\left[\ln{\left(1-\alpha\right)}\right]^{2/3}$

def A3(a, integral = False):
    """
    Avrami-Erofeev (A3) model 
    
    Parameters:   a : (\alpha) Conversion degree value.
    
    Returns:    f(a): Reaction model evaluated on the conversion degree
    """
    if integral == True:
        return (-np.log(1-a))**(1/3)
    else:
        return 3*(1-a)*((-np.log(1-a))**(2/3))

### A2: $f\left(\alpha\right) = 2\left(1-\alpha\right)\left[\ln{\left(1-\alpha\right)}\right]^{1/2}$

def A2(a, integral = False):
    """
    Avrami-Erofeev (A2) model 
    
    Parameters:   a : (\alpha) Conversion degree value.
    
    Returns:    f(a): Reaction model evaluated on the conversion degree
    """
    if integral == True:
        return (-np.log(1-a))**(1/2)
    else:
        return 2*(1-a)*((-np.log(1-a))**(1/2))

### G4: $f\left(\alpha\right) = (1/2)(1 - a)/[- ln(1 - a)]$

def G4(a, integral = False):
    """
    G4 model 
    
    Parameters:   a : (\alpha) Conversion degree value.
    
    Returns:    f(a): Reaction model evaluated on the conversion degree
    """
    if integral == True:
        return (- np.log(1 - a))**2
    else:
        return (1/2)*(1 - a) / (- np.log(1 - a))

### G5: $f\left(\alpha\right) = (1/3)(1 - a)/[- ln(1 - a)]^2$

def G5(a, integral = False):
    """
    G5 model 
    
    Parameters:   a : (\alpha) Conversion degree value.
    
    Returns:    f(a): Reaction model evaluated on the conversion degree
    """
    if integral == True:
        return (- np.log(1 - a))**3
    else:
        return (1/3)*(1 - a) / ((- np.log(1 - a))**2)

### G6: $f\left(\alpha\right) = (1/4)(1 - a)/[- ln(1 - a)]^3$

def G6(a, integral = False):
    """
    G6 model 
    
    Parameters:   a : (\alpha) Conversion degree value.
    
    Returns:    f(a): Reaction model evaluated on the conversion degree
    """
    if integral == True:
        return (- np.log(1 - a))**4
    else:
        return (1/4)*(1 - a) / ((- np.log(1 - a))**3)

## Contractions

### Contracting sphere (R3): $f\left(\alpha\right) = 3\left(1-\alpha\right)^{2/3}$

def R3(a, integral =  False):
    """
    Contracting sphere (R3) model 
    
    Parameters:   a : (\alpha) Conversion degree value.
    
    Returns:    f(a): Reaction model evaluated on the conversion degree
    """
    if integral == True:
        return 1 - ((1-a)**(1/3))
    else:
        return 3*((1-a)**(2/3))

### Contracting cylinder (R2): $f\left(\alpha\right) = 2\left(1-\alpha\right)^{1/2}$

def R2(a, integral =  False):
    """
    Contracting cylinder (R2) model 
    
    Parameters:   a : (\alpha) Conversion degree value.
    
    Returns:    f(a): Reaction model evaluated on the conversion degree
    """
    if integral == True:
        return 1 - ((1-a)**(1/2))
    else:
        return 2*((1-a)**(1/2))
