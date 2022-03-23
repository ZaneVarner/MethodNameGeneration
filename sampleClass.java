/**
 * Vehicle class (superclass).
 */
class Vehicle {
    protected String brand = "Ford";
   
    /**
     * honk honk honk honk method (superclass' method).
     */
    public void honk() {                    
        System.out.println("Tuut, tuut!");
    }
}

/**
 * Car class (subclass).
 */
class Car extends Vehicle {
    private String modelName = "Mustang";    

    /**
     * main fnc of Car.
     */
    public static void main(String[] args) {

        Car myCar = new Car();
        Vehicle myVehicle = new Vehicle();

        super.honk();
        String carBrand = super.brand;

        myCar.honk();

        System.out.println(myCar.brand + " " + myCar.modelName);
    }
}