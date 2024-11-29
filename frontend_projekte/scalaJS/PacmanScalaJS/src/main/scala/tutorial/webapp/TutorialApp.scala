/*
Authors: 
	Tamer Özdemir, Matrikelnummer: 5507971, Email: tamer.oezdemir@student.uni-tuebingen.de
	Enes Eminovic, Matrikelnummer: 5410611, Email: enes.eminovic@student.uni-tuebingen.de
*/

package tutorial.webapp
import org.scalajs.dom
import org.scalajs.dom.document
import scala.scalajs.js.annotation.JSExportTopLevel
import scala.scalajs.js.annotation.JSExport
import org.scalajs.dom.html
import scala.annotation.meta.field
import scala.util.Random

object TutorialApp {

	//Pacman class with position, direction and a drawfunction

	class Pacman(x: Int, y: Int){
		var posX: Int = x * 20
		var posY: Int = y * 20

		var direction: String = ""

		def draw(ctx: dom.CanvasRenderingContext2D, direction: String) : Unit = {
			if(direction == "start") {
				ctx.fillStyle = "yellow"
    			ctx.fillRect(posX, posY, 20, 20)
			}
			
			if(direction == "right") {
				ctx.fillStyle = "yellow"
    			ctx.fillRect(posX, posY, 20, 20)
				ctx.fillStyle = "black"
				ctx.fillRect(posX-5, posY, 5, 20) 	
			}
			if(direction == "up") {
				ctx.fillStyle = "yellow"
    			ctx.fillRect(posX, posY, 20, 20)
				ctx.fillStyle = "black"
				ctx.fillRect(posX, posY+20, 20, 5) 	
			}
			if(direction == "left") {
				ctx.fillStyle = "yellow"
    			ctx.fillRect(posX, posY, 20, 20)
				ctx.fillStyle = "black"
				ctx.fillRect(posX+20, posY, 5, 20) 	
			}
			if(direction == "down") {
				ctx.fillStyle = "yellow"
    			ctx.fillRect(posX, posY, 20, 20)
				ctx.fillStyle = "black"
				ctx.fillRect(posX, posY-5, 20, 5) 	
			}
		}
	}
	//Ghost class with position, direction, color, draw function and movement function
	class Ghost(x: Int, y: Int, c: String){
		var posX: Int = x * 20
		var posY: Int = y * 20

		var direction: String = "right"
		var color: String = c

		def draw(ctx: dom.CanvasRenderingContext2D, direction: String) : Unit = {
			if(direction == "start") {
				ctx.fillStyle = color
    			ctx.fillRect(posX, posY, 20, 20)
			}
			
			if(direction == "right") {
				ctx.fillStyle = color
    			ctx.fillRect(posX, posY, 20, 20)
				ctx.fillStyle = "black"
				ctx.fillRect(posX-5, posY, 5, 20) 	
			}
			if(direction == "up") {
				ctx.fillStyle = color
    			ctx.fillRect(posX, posY, 20, 20)
				ctx.fillStyle = "black"
				ctx.fillRect(posX, posY+20, 20, 5) 	
			}
			if(direction == "left") {
				ctx.fillStyle = color
    			ctx.fillRect(posX, posY, 20, 20)
				ctx.fillStyle = "black"
				ctx.fillRect(posX+20, posY, 5, 20) 	
			}
			if(direction == "down") {
				ctx.fillStyle = color
    			ctx.fillRect(posX, posY, 20, 20)
				ctx.fillStyle = "black"
				ctx.fillRect(posX, posY-5, 20, 5) 	
			}
		}


		//Ghosts moving on their own
		def ghostMovement() : Unit = {
			var step = true

			var directions = Array(("left", true), ("up", true), ("right", true), ("down", true))
			var possibleDirections = Array[String]()

			this.direction match {
				case "left" =>
					//Collision checking with walls, if there is a wall, draw the object at the same place
					if(this.posX > 0) {
						for(i <- 0 to walls.length - 1) {
							if(this.posX == walls(i)._1 + 20 && (this.posY >= walls(i)._2-19 &&  this.posY <= walls(i)._2+19)) {
								step = false
								
							}
						}
						if(step == true) {
							this.posX -= 5
							this.draw(ctx, "left")
							
						}
						else{
							this.posX -= 0
							this.draw(ctx, "start")
						}
					} 
					else {
						this.posX -= 0
						this.draw(ctx, "start")
					}

					//Decision for next movement
					for(i <- 0 to walls.length -1) {
						if(this.posY == 0 || (this.posY == walls(i)._2 + 20 && (this.posX >= walls(i)._1-19 &&  this.posX <= walls(i)._1+19))) {
							directions(1) = ("up", false)
						}
						if(this.posY == 240 || (this.posY+20 == walls(i)._2 && (this.posX >= walls(i)._1-19 &&  this.posX <= walls(i)._1+19))) {
							directions(3) = ("down", false)
						}
						if(this.posX == 0 || (this.posX == walls(i)._1 + 20 && (this.posY >= walls(i)._2-19 &&  this.posY <= walls(i)._2+19))) {
							directions(0) = ("left", false)
						}
					}

					for(i <- 0 to directions.length - 1){
						if(directions(i)._2 == true && directions(i)._1 != "right") {
							possibleDirections = possibleDirections.appended(directions(i)._1)
						}
					}
					if (possibleDirections.length != 0) {
						this.direction = Random.shuffle(possibleDirections.toList).head
					}
					else {
						this.direction = "right"
					}
					
					
				case "up" =>
					//Collision checking with walls, if there is a wall, draw the object at the same place
					if(this.posY > 0) {
						for(i <- 0 to walls.length - 1) {
							if(this.posY == walls(i)._2 + 20 && (this.posX >= walls(i)._1-19 &&  this.posX <= walls(i)._1+19)) {
								step = false
								
							}
						}
						if(step == true) {
							this.posY -= 5
							this.draw(ctx, "up")		
						}
						else{
							this.posY -= 0
							this.draw(ctx, "start")
						}
					}
					else {
						this.posY -= 0
						this.draw(ctx, "start")
					}
					//Decision for next movement
					for(i <- 0 to walls.length -1) {
						if(this.posY == 0 || (this.posY == walls(i)._2 + 20 && (this.posX >= walls(i)._1-19 &&  this.posX <= walls(i)._1+19))) {
							directions(1) = ("up", false)
						}
						if(this.posX == 280 || (this.posX+20 == walls(i)._1 && (this.posY >= walls(i)._2-19 && this.posY <= walls(i)._2+19))) {
							directions(2) = ("right", false)
						}
						if(this.posX == 0 || (this.posX == walls(i)._1 + 20 && (this.posY >= walls(i)._2-19 &&  this.posY <= walls(i)._2+19))) {
							directions(0) = ("left", false)
						}
					}

					for(i <- 0 to directions.length - 1){
						if(directions(i)._2 == true && directions(i)._1 != "down") {
							possibleDirections = possibleDirections.appended(directions(i)._1)
						}
					}
					if (possibleDirections.length != 0) {
						this.direction = Random.shuffle(possibleDirections.toList).head
					}
					else {
						this.direction = "down"
					}
					
				case "right" =>
					//Collision checking with walls, if there is a wall, draw the object at the same place
					if(this.posX < 280) {
						for(i <- 0 to walls.length - 1) {
							if(this.posX+20 == walls(i)._1 && (this.posY >= walls(i)._2-19 && this.posY <= walls(i)._2+19)) {
								step = false
								
							}
						}
						if(step == true) {
							this.posX += 5
							this.draw(ctx, "right")		
						}
						else{
							this.posX += 0
							this.draw(ctx, "start")
						}
						
					} 
					else {
						this.posX += 0
						this.draw(ctx, "start")
					}
					//Decision for next movement
					for(i <- 0 to walls.length -1) {
						if(this.posY == 0 || (this.posY == walls(i)._2 + 20 && (this.posX >= walls(i)._1-19 &&  this.posX <= walls(i)._1+19))) {
							directions(1) = ("up", false)
						}
						if(this.posY == 240 || (this.posY+20 == walls(i)._2 && (this.posX >= walls(i)._1-19 &&  this.posX <= walls(i)._1+19))) {
							directions(3) = ("down", false)
						}
						if(this.posX == 280 || (this.posX+20 == walls(i)._1 && (this.posY >= walls(i)._2-19 && this.posY <= walls(i)._2+19))) {
							directions(2) = ("right", false)
						}
					}

					for(i <- 0 to directions.length - 1){
						if(directions(i)._2 == true && directions(i)._1 != "left") {
							possibleDirections = possibleDirections.appended(directions(i)._1)
						}
					}
					if (possibleDirections.length != 0) {
						this.direction = Random.shuffle(possibleDirections.toList).head
					}
					else {
						this.direction = "left"
					}
					
				case "down" =>
					//Collision checking with walls, if there is a wall, draw the object at the same place 
					if(this.posY < 240) {
						for(i <- 0 to walls.length - 1) {
							if(this.posY+20 == walls(i)._2 && (this.posX >= walls(i)._1-19 &&  this.posX <= walls(i)._1+19)) {
								step = false
							}
						}
						if(step == true) {
							this.posY += 5
							this.draw(ctx, "down")		
						}
						else{
							this.posY += 0
							this.draw(ctx, "start")
						}
					}
					else {
						this.posY += 0
						this.draw(ctx, "start")
					}
					//Decision for next movement
					for(i <- 0 to walls.length -1) {
						if(this.posY == 240 || (this.posY+20 == walls(i)._2 && (this.posX >= walls(i)._1-19 &&  this.posX <= walls(i)._1+19))) {
							directions(3) = ("down", false)
						}
						if(this.posX == 280 || (this.posX+20 == walls(i)._1 && (this.posY >= walls(i)._2-19 && this.posY <= walls(i)._2+19))) {
							directions(2) = ("right", false)
						}
						if(this.posX == 0 || (this.posX == walls(i)._1 + 20 && (this.posY >= walls(i)._2-19 &&  this.posY <= walls(i)._2+19))) {
							directions(0) = ("left", false)
						}
					}

					for(i <- 0 to directions.length - 1){
						if(directions(i)._2 == true && directions(i)._1 != "up") {
							possibleDirections = possibleDirections.appended(directions(i)._1)
						}
					}
					if (possibleDirections.length != 0) {
						this.direction = Random.shuffle(possibleDirections.toList).head
					}
					else {
						this.direction = "up"
					}
				case _ =>

			//Checking if a collision with pacman is true, if yes, set life to 0		
			}
			if((this.posX+20 >= pacMan.posX && this.posX <= pacMan.posX +20 && this.posY == pacMan.posY) || (this.posY+20 >= pacMan.posY && this.posY <= pacMan.posY +20 && this.posX == pacMan.posX)) {
				live -= 1 
			}
		}
	}

	

	//Function to draw each pellet again after every single interval in the game (Because Ghosts can't eat pellets)
	def drawPellets() : Unit = {
		for(i <- 0 to pellets.length - 1) {
			if(pellets(i)._1 != -1){
				if(((pellets(i)._1 >= ghost1.posX+20  || pellets(i)._1  <= ghost1.posX ) && (pellets(i)._2  >= ghost1.posY  || pellets(i)._2  <= ghost1.posY) ||
					(pellets(i)._1 >= ghost1.posX  || pellets(i)._1  <= ghost1.posX ) && (pellets(i)._2  >= ghost1.posY +20 || pellets(i)._2  <= ghost1.posY)) &&
					((pellets(i)._1 >= ghost2.posX+20  || pellets(i)._1  <= ghost2.posX ) && (pellets(i)._2  >= ghost2.posY  || pellets(i)._2  <= ghost2.posY) ||
					(pellets(i)._1 >= ghost2.posX  || pellets(i)._1  <= ghost2.posX ) && (pellets(i)._2  >= ghost2.posY +20 || pellets(i)._2  <= ghost2.posY)) &&
					((pellets(i)._1 >= ghost3.posX+20  || pellets(i)._1  <= ghost3.posX ) && (pellets(i)._2  >= ghost3.posY  || pellets(i)._2  <= ghost3.posY) ||
					(pellets(i)._1 >= ghost3.posX  || pellets(i)._1  <= ghost3.posX ) && (pellets(i)._2  >= ghost3.posY +20 || pellets(i)._2  <= ghost3.posY))) {
					ctx.fillStyle = "white"
					ctx.beginPath()
					ctx.arc(pellets(i)._1, pellets(i)._2, 3, 0, math.Pi * 2)
					ctx.fill()
					ctx.closePath()
				}
				
			}
			
		}
	}
	//Movement of the PacMan, collision handling with walls and pellets
	def pacManMovement() : Unit = {
		var step = true
		pacMan.direction match {
			case "left" =>
				//Checking for collision with walls 
				if(pacMan.posX > 0) {
					for(i <- 0 to walls.length - 1) {
						if(pacMan.posX == walls(i)._1 + 20 && (pacMan.posY >= walls(i)._2-19 &&  pacMan.posY <= walls(i)._2+19)) {
							step = false
								
						}
					}
					if(step == true) {
						pacMan.posX -= 5
						pacMan.draw(ctx, "left")
						//Checking for collision with pellet
						for(i <- 0 to pellets.length -1) {
							if(pacMan.posX == pellets(i)._1 && pacMan.posY+10 == pellets(i)._2){
								score -= 1
								ctx.fillStyle = "black"
								ctx.fillRect(pacMan.posX-3, pacMan.posY, 3, 20)
								pellets(i) = (-1, -1)
							}
						}	
					}
					else{
						pacMan.posX -= 0
						pacMan.draw(ctx, "start")
					}
				} 
				else {
					pacMan.posX -= 0
					pacMan.draw(ctx, "start")
				}
			case "up" =>
				//Checking for collision with walls
				if(pacMan.posY > 0) {
					for(i <- 0 to walls.length - 1) {
						if(pacMan.posY == walls(i)._2 + 20 && (pacMan.posX >= walls(i)._1-19 &&  pacMan.posX <= walls(i)._1+19)) {
							step = false
								
						}
					}
					if(step == true) {
						pacMan.posY -= 5
						pacMan.draw(ctx, "up")
						//Checking for collision with pellet
						for(i <- 0 to pellets.length -1) {
							if(pacMan.posX+10 == pellets(i)._1 && pacMan.posY== pellets(i)._2){
								score -= 1
								ctx.fillStyle = "black"
								ctx.fillRect(pacMan.posX, pacMan.posY-3, 20, 3)
								pellets(i) = (-1, -1)
							}
						}		
					}
					else{
						pacMan.posY -= 0
						pacMan.draw(ctx, "start")
					}
				}
				else {
					pacMan.posY -= 0
					pacMan.draw(ctx, "start")
				}
			case "right" =>
				//Checking for collision with walls
				if(pacMan.posX < 280) {
					for(i <- 0 to walls.length - 1) {
						if(pacMan.posX+20 == walls(i)._1 && (pacMan.posY >= walls(i)._2-19 &&  pacMan.posY <= walls(i)._2+19)) {
							step = false
								
						}
					}
					if(step == true) {
						pacMan.posX += 5
						pacMan.draw(ctx, "right")
						//Checking for collision with pellet
						for(i <- 0 to pellets.length -1) {
							if(pacMan.posX+20 == pellets(i)._1 && pacMan.posY+10 == pellets(i)._2){
								score -= 1
								ctx.fillStyle = "black"
								ctx.fillRect(pacMan.posX+20, pacMan.posY, 3, 20)
								pellets(i) = (-1, -1)
							}
						}
								
					}
					else{
						pacMan.posX += 0
						pacMan.draw(ctx, "start")
					}
						
				} 
				else {
					pacMan.posX += 0
					pacMan.draw(ctx, "start")
				}
			case "down" =>
				//Checking for collision with walls 
				if(pacMan.posY < 240) {
					for(i <- 0 to walls.length - 1) {
						if(pacMan.posY+20 == walls(i)._2 && (pacMan.posX >= walls(i)._1-19 &&  pacMan.posX <= walls(i)._1+19)) {
							step = false
						}
					}
					if(step == true) {
						pacMan.posY += 5
						pacMan.draw(ctx, "down")
						//Checking for collision with pellet
						for(i <- 0 to pellets.length -1) {
							if(pacMan.posX+10 == pellets(i)._1 && pacMan.posY+20== pellets(i)._2){
								score -= 1
								ctx.fillStyle = "black"
								ctx.fillRect(pacMan.posX, pacMan.posY+20, 20, 3)
								pellets(i) = (-1, -1)
							}
						}		
					}
					else{
						pacMan.posY += 0
						pacMan.draw(ctx, "start")
					}
				}
				else {
					pacMan.posY += 0
					pacMan.draw(ctx, "start")
				}
			case _ => 	
		}
	}

	//Creating the scoreboard
	val scorePTag = dom.document.createElement("p").asInstanceOf[html.Paragraph]
	dom.document.body.appendChild(scorePTag)

	def setScore() {
		scorePTag.textContent= s"Pellets left: $score"
	}

	//This is our mainloop, calling all necessary functions to run the game 
	def update = {
		if(live > 0 && score > 0) {
			pacManMovement()
			ghost1.ghostMovement()
			ghost2.ghostMovement()
			ghost3.ghostMovement()
			drawPellets()
			setScore()
		}
		else{
			if(live == 0) {
				scorePTag.textContent = s"You lost!"
			}
			else{
				scorePTag.textContent = s"You won!"
			}	
		}
	}

	//Creating the Canvas Area
	val canvas = dom.document.createElement("canvas").asInstanceOf[dom.HTMLCanvasElement]
	canvas.width = 300
	canvas.height = 260
	canvas.style.border = "5px solid blue"
	dom.document.body.appendChild(canvas)

	var live = 1

	val ctx = canvas.getContext("2d").asInstanceOf[dom.CanvasRenderingContext2D]

	val pacMan = new Pacman(0, 0)
	val ghost1 = new Ghost(6, 4, "red")
	val ghost2 = new Ghost(7, 4, "pink")
	val ghost3 = new Ghost(8, 4, "green")
	
	//Creating the Gamefield
	var score = 0
	var pellets = Array[(Int, Int)]()
	var walls = Array[(Int, Int)]()

	def initializeField() : Unit = {
		val rows = 300 / 20
		val cols = 260 / 20

		var field = Array(Array(3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
						  Array(0, 1, 0, 1, 1, 1, 0, 1, 0, 1, 1, 1, 0, 1, 0),
						  Array(0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0),
						  Array(0, 1, 0, 0, 0, 1, 1, 2, 1, 1, 0, 0, 0, 1, 0),
						  Array(0, 1, 0, 1, 0, 1, 3, 3, 3, 1, 0, 1, 0, 1, 0),
						  Array(0, 1, 0, 1, 0, 1, 1, 1, 1, 1, 0, 1, 0, 1, 0),
						  Array(0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0),
						  Array(0, 1, 0, 1, 0, 1, 1, 1, 1, 1, 0, 1, 0, 1, 0),
						  Array(0, 1, 0, 1, 0, 1, 0, 0, 0, 1, 0, 1, 0, 1, 0),
						  Array(0, 1, 0, 0, 0, 1, 0, 1, 0, 1, 0, 0, 0, 1, 0),
						  Array(0, 1, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 1, 0),
						  Array(0, 1, 0, 1, 1, 1, 0, 1, 0, 1, 1, 1, 0, 1, 0),
						  Array(0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0))	
		
		for(a <- 0 to rows - 1) {
			for(b <- 0 to cols-1) {
				if(field(b)(a) == 0){
					ctx.fillStyle = "white"
					ctx.beginPath()
					ctx.arc(20*a+10, 20*b+10, 3, 0, math.Pi * 2)
					ctx.fill()
					ctx.closePath()
					pellets = pellets.appended(((20*a+10, 20*b+10)))
				}
				if(field(b)(a) == 1) {
					ctx.fillStyle = "blue"
					ctx.fillRect(20*a, 20*b, 20, 20)
					walls = walls.appended((20*a, 20*b))
				}
			}
		}
		pacMan.draw(ctx, "start")
		ghost1.draw(ctx, "start")
		ghost2.draw(ctx, "start")
		ghost3.draw(ctx, "start")

		score = pellets.length
	}

	def main(args: Array[String]): Unit = {
		ctx.fillStyle = "black"
		ctx.fillRect(0, 0, 300, 260)
		initializeField()
		//This is our Intervalfunction which calls the mainloop function "update"
		dom.window.setInterval(() => update, 50)
	}

	//Eventhandler for pressing arrowkeys to change direction of the pacman
	dom.document.addEventListener("keydown", (e: dom.KeyboardEvent) => {
		e.keyCode match {
			case 37 => pacMan.direction = "left"
			case 38 => pacMan.direction = "up"
			case 39 => pacMan.direction = "right"
			case 40 => pacMan.direction = "down"
		}
	})	
}
	
